"""
Wayback Machine Plugin - Historical website data
API: https://archive.org/help/wayback_api.php
"""

import aiohttp
from typing import Dict
from datetime import datetime, timedelta
from plugins import PythonPlugin


class Plugin(PythonPlugin):
    """
    Wayback Machine - Historical website snapshots and URLs
    
    Free API, no key required
    Access historical website data
    """
    
    async def execute(self) -> Dict:
        """Query Wayback Machine API"""
        findings = {
            'urls': [],
            'snapshots': [],
            'domains': []
        }
        
        domain = self._extract_domain_from_target()
        if not domain:
            domain = self.target
        
        findings['domains'].append(domain)
        
        try:
            # Get URL list
            urls = await self._get_urls(domain)
            findings['urls'] = urls
            
            # Get snapshots
            snapshots = await self._get_snapshots(domain)
            findings['snapshots'] = snapshots
        
        except Exception as e:
            findings['error'] = str(e)
        
        return findings
    
    async def _get_urls(self, domain: str) -> list:
        """Get list of URLs from CDX API"""
        url = f"http://web.archive.org/cdx/search/cdx"
        
        params = {
            'url': f'*.{domain}/*',
            'output': 'json',
            'fl': 'original,timestamp,statuscode',
            'collapse': 'urlkey',
            'limit': self.config.get('limit', 1000)
        }
        
        urls = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Skip header row
                        for row in data[1:]:
                            if len(row) >= 3:
                                original_url = row[0]
                                timestamp = row[1]
                                status_code = row[2]
                                
                                urls.append({
                                    'url': original_url,
                                    'timestamp': timestamp,
                                    'status': status_code
                                })
        except Exception:
            pass
        
        return urls
    
    async def _get_snapshots(self, domain: str) -> list:
        """Get snapshot availability"""
        url = f"http://archive.org/wayback/available"
        
        params = {
            'url': domain
        }
        
        snapshots = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('archived_snapshots'):
                            closest = data['archived_snapshots'].get('closest')
                            if closest:
                                snapshots.append({
                                    'url': closest.get('url'),
                                    'timestamp': closest.get('timestamp'),
                                    'status': closest.get('status'),
                                    'available': closest.get('available')
                                })
        except Exception:
            pass
        
        return snapshots


# Standalone execution
if __name__ == '__main__':
    import asyncio
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python wayback_plugin.py <domain>")
        sys.exit(1)
    
    plugin = Plugin(target=sys.argv[1])
    result = asyncio.run(plugin.run())
    print(json.dumps(result, indent=2))
