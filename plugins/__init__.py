"""
PHINEAS Plugin Base Classes
Abstract base for all OSINT plugins
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PluginBase(ABC):
    """
    Abstract base class for all PHINEAS plugins
    
    All plugins must inherit from this class and implement the run() method
    """
    
    def __init__(self, target: str, config: Dict = None, api_keys: Dict = None):
        self.target = target
        self.config = config or {}
        self.api_keys = api_keys or {}
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    @abstractmethod
    async def run(self) -> Dict:
        """
        Execute the plugin
        
        Returns:
            Dict with structure:
            {
                'status': 'success' | 'failed',
                'plugin': 'plugin_name',
                'target': 'target_identifier',
                'findings': {...},
                'metadata': {...},
                'error': 'error_message' (if failed)
            }
        """
        pass
    
    def _create_result(self, status: str, findings: Dict = None, error: str = None) -> Dict:
        """Helper to create standardized result dictionary"""
        self.end_time = datetime.now()
        
        result = {
            'status': status,
            'plugin': self.__class__.__name__,
            'target': self.target,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat(),
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.start_time else 0,
            'findings': findings or {},
            'metadata': self.config
        }
        
        if error:
            result['error'] = error
        
        return result
    
    async def execute_command(self, command: List[str], timeout: int = 300) -> tuple:
        """
        Execute an external command asynchronously
        
        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return (
                stdout.decode('utf-8', errors='ignore'),
                stderr.decode('utf-8', errors='ignore'),
                process.returncode
            )
        
        except asyncio.TimeoutError:
            logger.error(f"Command timeout: {' '.join(command)}")
            return ('', 'Command timeout', -1)
        except Exception as e:
            logger.error(f"Command error: {e}")
            return ('', str(e), -1)
    
    def _extract_email_from_target(self) -> Optional[str]:
        """Extract email if target is an email address"""
        if '@' in self.target:
            return self.target
        return None
    
    def _extract_username_from_email(self) -> Optional[str]:
        """Extract username from email address"""
        if '@' in self.target:
            return self.target.split('@')[0]
        return None
    
    def _extract_domain_from_target(self) -> Optional[str]:
        """Extract domain from email or URL"""
        if '@' in self.target:
            return self.target.split('@')[1]
        elif self.target.startswith('http'):
            from urllib.parse import urlparse
            return urlparse(self.target).netloc
        elif '.' in self.target:
            return self.target
        return None
    
    def get_timeout(self) -> int:
        """Get timeout from config or use default"""
        return self.config.get('timeout', 300)
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return not self.config.get('disabled', False)


class CommandLinePlugin(PluginBase):
    """Base class for plugins that wrap command-line tools"""
    
    @abstractmethod
    def get_command(self) -> List[str]:
        """Return the command to execute"""
        pass
    
    @abstractmethod
    def parse_output(self, stdout: str, stderr: str) -> Dict:
        """Parse command output into structured findings"""
        pass
    
    async def run(self) -> Dict:
        """Execute command-line tool and parse results"""
        self.start_time = datetime.now()
        
        try:
            command = self.get_command()
            timeout = self.get_timeout()
            
            stdout, stderr, returncode = await self.execute_command(command, timeout)
            
            if returncode != 0 and not stdout:
                return self._create_result('failed', error=f"Command failed: {stderr}")
            
            findings = self.parse_output(stdout, stderr)
            return self._create_result('success', findings=findings)
        
        except Exception as e:
            logger.error(f"Plugin error: {e}")
            return self._create_result('failed', error=str(e))


class APIPlugin(PluginBase):
    """Base class for plugins that use API calls"""
    
    def __init__(self, target: str, config: Dict = None, api_keys: Dict = None):
        super().__init__(target, config, api_keys)
        self.api_key = self._get_api_key()
    
    @abstractmethod
    def get_api_key_name(self) -> str:
        """Return the API key name for this plugin"""
        pass
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key for this plugin"""
        key_name = self.get_api_key_name()
        return self.api_keys.get(key_name)
    
    def has_api_key(self) -> bool:
        """Check if API key is configured"""
        return self.api_key is not None
    
    async def run(self) -> Dict:
        """Execute API plugin with key validation"""
        if not self.has_api_key():
            return self._create_result(
                'failed',
                error=f"API key not configured for {self.get_api_key_name()}"
            )
        
        return await self.execute_api_call()
    
    @abstractmethod
    async def execute_api_call(self) -> Dict:
        """Execute the API call and return results"""
        pass


class PythonPlugin(PluginBase):
    """Base class for plugins that use Python libraries"""
    
    async def run(self) -> Dict:
        """Execute Python-based plugin"""
        self.start_time = datetime.now()
        
        try:
            findings = await self.execute()
            return self._create_result('success', findings=findings)
        except Exception as e:
            logger.error(f"Plugin error: {e}")
            return self._create_result('failed', error=str(e))
    
    @abstractmethod
    async def execute(self) -> Dict:
        """Execute the plugin logic"""
        pass
