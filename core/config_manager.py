#!/usr/bin/env python3
"""
PHINEAS Configuration Manager
Handles API keys, credentials, and configuration
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import keyring


class ConfigManager:
    """
    Manages PHINEAS configuration, API keys, and credentials
    
    Supports multiple storage backends:
    - Environment variables (.env)
    - YAML config files
    - System keyring (secure storage)
    - Cronos ops.json integration
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / '.phineas'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / 'config.yaml'
        self.env_file = self.config_dir / '.env'
        
        # Load environment variables
        load_dotenv(self.env_file)
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return yaml.safe_load(f) or {}
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'version': '1.0.0',
            'output_dir': './phineas-results',
            'concurrent_scans': 5,
            'timeout': 300,
            'retry_failed': True,
            'max_retries': 2,
            'api_keys': {},
            'plugins': {
                'enabled': [],
                'disabled': []
            },
            'integrations': {
                'cronos': {
                    'enabled': False,
                    'db_host': 'localhost',
                    'db_port': 5432,
                    'db_name': 'cronos'
                }
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service
        
        Priority:
        1. Environment variable
        2. System keyring
        3. Config file
        4. Cronos ops.json
        """
        # 1. Check environment variable
        env_var = f"PHINEAS_{service.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        if api_key:
            return api_key
        
        # 2. Check system keyring
        try:
            api_key = keyring.get_password('phineas', service)
            if api_key:
                return api_key
        except Exception:
            pass
        
        # 3. Check config file
        api_key = self.config.get('api_keys', {}).get(service, {})
        if isinstance(api_key, dict):
            return api_key.get('key')
        elif isinstance(api_key, str):
            return api_key
        
        # 4. Check Cronos ops.json
        cronos_key = self._get_cronos_api_key(service)
        if cronos_key:
            return cronos_key
        
        return None
    
    def _get_cronos_api_key(self, service: str) -> Optional[str]:
        """Get API key from Cronos ops.json"""
        # Try multiple locations
        possible_paths = [
            Path('D:/HAK/cptp-manual/security-scanning/config/ops.json'),
            Path('./config/ops.json'),
            Path('../security-scanning/config/ops.json')
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path) as f:
                        ops_config = json.load(f)
                        api_keys = ops_config.get('api_keys', {})
                        service_config = api_keys.get(service, {})
                        if isinstance(service_config, dict) and service_config.get('api_key'):
                            return service_config['api_key']
                except Exception:
                    continue
        
        return None
    
    def set_api_key(self, service: str, api_key: str, storage: str = 'keyring'):
        """
        Set API key for a service
        
        Args:
            service: Service name (shodan, haveibeenpwned, etc.)
            api_key: API key value
            storage: Storage backend ('keyring', 'env', 'config')
        """
        if storage == 'keyring':
            keyring.set_password('phineas', service, api_key)
        elif storage == 'env':
            # Append to .env file
            with open(self.env_file, 'a') as f:
                f.write(f"\nPHINEAS_{service.upper()}_API_KEY={api_key}\n")
        elif storage == 'config':
            if 'api_keys' not in self.config:
                self.config['api_keys'] = {}
            self.config['api_keys'][service] = api_key
            self.save_config()
    
    def remove_api_key(self, service: str):
        """Remove API key from all storage locations"""
        try:
            keyring.delete_password('phineas', service)
        except Exception:
            pass
        
        # Remove from config
        if 'api_keys' in self.config and service in self.config['api_keys']:
            del self.config['api_keys'][service]
            self.save_config()
    
    def list_api_keys(self) -> Dict[str, bool]:
        """List configured API keys (without revealing values)"""
        services = [
            'shodan', 'securitytrails', 'haveibeenpwned', 'virustotal',
            'hunter', 'snusbase', 'dehashed', 'censys', 'github',
            'twitter', 'numverify', 'clearbit'
        ]
        
        status = {}
        for service in services:
            status[service] = self.get_api_key(service) is not None
        
        return status
    
    def interactive_setup(self):
        """Interactive configuration setup"""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        
        console = Console()
        
        console.print("[bold cyan]PHINEAS Configuration Setup[/bold cyan]\n")
        
        # API Keys
        console.print("[yellow]API Key Configuration[/yellow]")
        console.print("Enter API keys for services (press Enter to skip):\n")
        
        services = {
            'shodan': 'Shodan (https://shodan.io) - Free tier: 1 query/month',
            'haveibeenpwned': 'Have I Been Pwned (https://haveibeenpwned.com/API/Key)',
            'securitytrails': 'SecurityTrails (https://securitytrails.com) - 50 queries/month',
            'virustotal': 'VirusTotal (https://virustotal.com) - 4 requests/min',
            'hunter': 'Hunter.io (https://hunter.io) - 25 searches/month',
            'github': 'GitHub Personal Access Token',
        }
        
        for service, description in services.items():
            console.print(f"\n[cyan]{service}[/cyan]: {description}")
            current = "configured" if self.get_api_key(service) else "not configured"
            console.print(f"Current status: [{current}]")
            
            if Confirm.ask(f"Configure {service}?", default=False):
                api_key = Prompt.ask("Enter API key", password=True)
                if api_key:
                    storage = Prompt.ask(
                        "Storage method",
                        choices=['keyring', 'env', 'config'],
                        default='keyring'
                    )
                    self.set_api_key(service, api_key, storage)
                    console.print(f"[green]OK[/green] {service} configured")
        
        # Output directory
        console.print("\n[yellow]Output Configuration[/yellow]")
        output_dir = Prompt.ask(
            "Results output directory",
            default=self.config.get('output_dir', './phineas-results')
        )
        self.config['output_dir'] = output_dir
        
        # Cronos integration
        console.print("\n[yellow]Cronos Integration[/yellow]")
        enable_cronos = Confirm.ask("Enable Cronos platform integration?", default=False)
        self.config['integrations']['cronos']['enabled'] = enable_cronos
        
        if enable_cronos:
            db_host = Prompt.ask("PostgreSQL host", default="localhost")
            db_port = Prompt.ask("PostgreSQL port", default="5432")
            db_name = Prompt.ask("Database name", default="cronos")
            
            self.config['integrations']['cronos'].update({
                'db_host': db_host,
                'db_port': int(db_port),
                'db_name': db_name
            })
        
        # Save configuration
        self.save_config()
        console.print("\n[bold green]Configuration saved![/bold green]")
        console.print(f"Config file: {self.config_file}")
    
    def get_plugin_config(self, plugin_name: str) -> Dict:
        """Get configuration for a specific plugin"""
        return self.config.get('plugins', {}).get(plugin_name, {})
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin"""
        if 'plugins' not in self.config:
            self.config['plugins'] = {'enabled': [], 'disabled': []}
        
        if plugin_name not in self.config['plugins']['enabled']:
            self.config['plugins']['enabled'].append(plugin_name)
        
        if plugin_name in self.config['plugins'].get('disabled', []):
            self.config['plugins']['disabled'].remove(plugin_name)
        
        self.save_config()
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin"""
        if 'plugins' not in self.config:
            self.config['plugins'] = {'enabled': [], 'disabled': []}
        
        if plugin_name not in self.config['plugins']['disabled']:
            self.config['plugins']['disabled'].append(plugin_name)
        
        if plugin_name in self.config['plugins'].get('enabled', []):
            self.config['plugins']['enabled'].remove(plugin_name)
        
        self.save_config()


def main():
    """CLI for config management"""
    import argparse
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    parser = argparse.ArgumentParser(description="PHINEAS Configuration Manager")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Interactive configuration setup')
    
    # List command
    subparsers.add_parser('list', help='List API key status')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set API key')
    set_parser.add_argument('service', help='Service name')
    set_parser.add_argument('key', help='API key value')
    set_parser.add_argument('--storage', choices=['keyring', 'env', 'config'], default='keyring')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove API key')
    remove_parser.add_argument('service', help='Service name')
    
    args = parser.parse_args()
    
    config_manager = ConfigManager()
    
    if args.command == 'setup':
        config_manager.interactive_setup()
    
    elif args.command == 'list':
        status = config_manager.list_api_keys()
        
        table = Table(title="API Key Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        
        for service, configured in status.items():
            status_text = "OK Configured" if configured else "X Not configured"
            style = "green" if configured else "red"
            table.add_row(service, f"[{style}]{status_text}[/{style}]")
        
        console.print(table)
    
    elif args.command == 'set':
        config_manager.set_api_key(args.service, args.key, args.storage)
        console.print(f"[green]OK[/green] API key for {args.service} configured")
    
    elif args.command == 'remove':
        config_manager.remove_api_key(args.service)
        console.print(f"[green]OK[/green] API key for {args.service} removed")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
