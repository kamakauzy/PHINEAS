"""
Holehe Plugin - Email to account finder
GitHub: https://github.com/megadose/holehe
"""

import json
import asyncio
from typing import Dict
from plugins import PythonPlugin


class Plugin(PythonPlugin):
    """
    Holehe - Check what sites are associated with an email
    
    Free tool, no API key required
    Checks 120+ platforms
    """
    
    async def execute(self) -> Dict:
        """Execute holehe using Python library"""
        findings = {
            'emails': [self.target],
            'accounts': [],
            'social_profiles': []
        }
        
        try:
            # Import holehe if available
            import holehe
            from holehe.core import *
            
            # Run holehe check
            results = await self._run_holehe_check()
            
            for site, data in results.items():
                if data.get('exists', False):
                    findings['accounts'].append(site)
                    
                    if data.get('url'):
                        findings['social_profiles'].append({
                            'platform': site,
                            'email': self.target,
                            'url': data.get('url'),
                            'exists': True,
                            'metadata': data
                        })
        
        except ImportError:
            # Fallback to command line
            return await self._run_command_line()
        except Exception as e:
            # Return partial results
            findings['error'] = str(e)
        
        return findings
    
    async def _run_holehe_check(self) -> Dict:
        """Run holehe check using library"""
        # This would use the holehe Python library
        # For now, we'll use command line
        return await self._run_command_line()
    
    async def _run_command_line(self) -> Dict:
        """Run holehe as command line tool"""
        command = ['holehe', self.target, '--only-used']
        
        stdout, stderr, returncode = await self.execute_command(command)
        
        findings = {
            'emails': [self.target],
            'accounts': [],
            'social_profiles': []
        }
        
        # Parse output
        for line in stdout.split('\n'):
            line = line.strip()
            
            # Look for [+] indicators
            if '[+]' in line or '✓' in line:
                # Extract platform name
                for word in line.split():
                    if word and not word.startswith('[') and word not in ['on', 'used']:
                        findings['accounts'].append(word)
                        findings['social_profiles'].append({
                            'platform': word,
                            'email': self.target,
                            'exists': True
                        })
                        break
        
        return findings


# Standalone execution
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python holehe_plugin.py <email>")
        sys.exit(1)
    
    plugin = Plugin(target=sys.argv[1])
    result = asyncio.run(plugin.run())
    print(json.dumps(result, indent=2))
