"""
Sublist3r Plugin - Subdomain enumeration
GitHub: https://github.com/aboul3la/Sublist3r
"""

import json
from typing import Dict, List
from plugins import CommandLinePlugin


class Plugin(CommandLinePlugin):
    """
    Sublist3r - Fast subdomain enumeration tool
    
    Free tool, no API key required
    Uses search engines and public sources
    """
    
    def get_command(self) -> List[str]:
        """Build sublist3r command"""
        domain = self._extract_domain_from_target()
        if not domain:
            domain = self.target
        
        command = [
            'sublist3r',
            '-d', domain,
            '-o', f'/tmp/sublist3r_{domain}.txt'
        ]
        
        # Add optional bruteforce (slower)
        if self.config.get('bruteforce', False):
            command.append('-b')
        
        # Add ports scan
        if self.config.get('scan_ports', False):
            command.extend(['-p', '80,443'])
        
        return command
    
    def parse_output(self, stdout: str, stderr: str) -> Dict:
        """Parse sublist3r output"""
        findings = {
            'domains': [],
            'subdomains': []
        }
        
        domain = self._extract_domain_from_target() or self.target
        findings['domains'].append(domain)
        
        # Parse stdout
        for line in stdout.split('\n'):
            line = line.strip()
            
            # Subdomains are printed as-is
            if '.' in line and domain in line:
                findings['subdomains'].append(line)
        
        # Try to read output file
        try:
            import os
            output_file = f'/tmp/sublist3r_{domain}.txt'
            
            if os.path.exists(output_file):
                with open(output_file) as f:
                    for line in f:
                        subdomain = line.strip()
                        if subdomain:
                            findings['subdomains'].append(subdomain)
        except Exception:
            pass
        
        # Deduplicate
        findings['subdomains'] = sorted(list(set(findings['subdomains'])))
        
        return findings


# Standalone execution
if __name__ == '__main__':
    import asyncio
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sublist3r_plugin.py <domain>")
        sys.exit(1)
    
    plugin = Plugin(target=sys.argv[1])
    result = asyncio.run(plugin.run())
    print(json.dumps(result, indent=2))
