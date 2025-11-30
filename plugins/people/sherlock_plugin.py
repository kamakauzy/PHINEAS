"""
Sherlock Plugin - Username enumeration across 300+ social networks
GitHub: https://github.com/sherlock-project/sherlock
"""

import json
from typing import Dict
from plugins import CommandLinePlugin


class Plugin(CommandLinePlugin):
    """
    Sherlock username search across social media platforms
    
    Free tool, no API key required
    Searches 300+ social networks
    """
    
    def get_command(self):
        """Build sherlock command"""
        # Extract username from target
        username = self.target
        if '@' in username:
            username = self._extract_username_from_email()
        
        command = ['sherlock', username, '--json', '--timeout', '10']
        
        # Add optional filters
        if self.config.get('sites_filter') == 'popular':
            command.extend(['--nsfw', 'False'])
        
        return command
    
    def parse_output(self, stdout: str, stderr: str) -> Dict:
        """Parse sherlock JSON output"""
        findings = {
            'usernames': [],
            'social_profiles': [],
            'accounts': []
        }
        
        try:
            # Sherlock outputs multiple JSON objects, one per username
            for line in stdout.strip().split('\n'):
                if line and line.startswith('{'):
                    data = json.loads(line)
                    
                    for platform, info in data.items():
                        if isinstance(info, dict) and info.get('url_user'):
                            findings['social_profiles'].append({
                                'platform': platform,
                                'username': info.get('url_user').split('/')[-1],
                                'url': info.get('url_user'),
                                'exists': True
                            })
                            
                            findings['accounts'].append(platform)
        
        except json.JSONDecodeError:
            # Fallback: parse text output
            for line in stdout.split('\n'):
                if '[+]' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        platform = parts[0].replace('[+]', '').strip()
                        url = parts[1].strip()
                        findings['social_profiles'].append({
                            'platform': platform,
                            'url': url,
                            'exists': True
                        })
        
        # Add target username to findings
        username = self.target
        if '@' in username:
            username = self._extract_username_from_email()
        findings['usernames'].append(username)
        
        return findings


# Standalone execution
if __name__ == '__main__':
    import asyncio
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sherlock_plugin.py <username>")
        sys.exit(1)
    
    plugin = Plugin(target=sys.argv[1])
    result = asyncio.run(plugin.run())
    print(json.dumps(result, indent=2))
