"""
theHarvester Plugin - Email, subdomain, and host enumeration
GitHub: https://github.com/laramies/theHarvester
"""

import json
from typing import Dict, List
from plugins import CommandLinePlugin


class Plugin(CommandLinePlugin):
    """
    theHarvester - Email and subdomain harvesting from public sources
    
    Free tool, no API key required for basic sources
    Supports: Google, Bing, LinkedIn, Twitter, and more
    """
    
    def get_command(self) -> List[str]:
        """Build theHarvester command"""
        domain = self._extract_domain_from_target()
        if not domain:
            domain = self.target
        
        # Default sources (no API key needed)
        sources = self.config.get('sources', ['google', 'bing', 'duckduckgo', 'yahoo'])
        sources_str = ','.join(sources)
        
        limit = self.config.get('limit', 500)
        
        command = [
            'theHarvester',
            '-d', domain,
            '-b', sources_str,
            '-l', str(limit),
            '-f', f'/tmp/harvester_{domain}.json'
        ]
        
        return command
    
    def parse_output(self, stdout: str, stderr: str) -> Dict:
        """Parse theHarvester output"""
        findings = {
            'emails': [],
            'subdomains': [],
            'hosts': [],
            'urls': []
        }
        
        # Parse text output
        current_section = None
        
        for line in stdout.split('\n'):
            line = line.strip()
            
            if 'Emails found:' in line:
                current_section = 'emails'
                continue
            elif 'Hosts found:' in line:
                current_section = 'hosts'
                continue
            elif 'Interesting' in line:
                current_section = 'urls'
                continue
            
            if not line or line.startswith('['):
                continue
            
            if current_section == 'emails':
                if '@' in line:
                    findings['emails'].append(line)
            elif current_section == 'hosts':
                if ':' in line:
                    parts = line.split(':')
                    host = parts[0].strip()
                    if '.' in host:
                        findings['subdomains'].append(host)
                        findings['hosts'].append(line)
            elif current_section == 'urls':
                if line.startswith('http'):
                    findings['urls'].append(line)
        
        # Try to read JSON output file if it exists
        try:
            domain = self._extract_domain_from_target() or self.target
            json_file = f'/tmp/harvester_{domain}.json'
            
            import os
            if os.path.exists(json_file):
                with open(json_file) as f:
                    data = json.load(f)
                    
                    if 'emails' in data:
                        findings['emails'].extend(data['emails'])
                    if 'hosts' in data:
                        findings['subdomains'].extend(data['hosts'])
        except Exception:
            pass
        
        # Deduplicate
        findings['emails'] = list(set(findings['emails']))
        findings['subdomains'] = list(set(findings['subdomains']))
        findings['hosts'] = list(set(findings['hosts']))
        findings['urls'] = list(set(findings['urls']))
        
        return findings


# Standalone execution
if __name__ == '__main__':
    import asyncio
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python harvester_plugin.py <domain>")
        sys.exit(1)
    
    plugin = Plugin(target=sys.argv[1])
    result = asyncio.run(plugin.run())
    print(json.dumps(result, indent=2))
