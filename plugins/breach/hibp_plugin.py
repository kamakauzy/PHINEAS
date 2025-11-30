"""
Have I Been Pwned Plugin - Check email breaches
API: https://haveibeenpwned.com/API/v3
"""

import aiohttp
from typing import Dict
from plugins import APIPlugin


class Plugin(APIPlugin):
    """
    Have I Been Pwned - Check if email appears in data breaches
    
    Requires free API key from https://haveibeenpwned.com/API/Key
    """
    
    def get_api_key_name(self) -> str:
        return 'haveibeenpwned'
    
    async def execute_api_call(self) -> Dict:
        """Query HIBP API"""
        findings = {
            'emails': [self.target],
            'breaches': [],
            'pastes': []
        }
        
        try:
            # Check breaches
            breaches = await self._check_breaches()
            findings['breaches'] = breaches
            
            # Check pastes (if API key allows)
            pastes = await self._check_pastes()
            findings['pastes'] = pastes
        
        except Exception as e:
            findings['error'] = str(e)
        
        return findings
    
    async def _check_breaches(self) -> list:
        """Check for breaches"""
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{self.target}"
        
        headers = {
            'hibp-api-key': self.api_key,
            'user-agent': 'PHINEAS-OSINT'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    breaches = []
                    for breach in data:
                        breaches.append({
                            'name': breach.get('Name'),
                            'title': breach.get('Title'),
                            'domain': breach.get('Domain'),
                            'breach_date': breach.get('BreachDate'),
                            'added_date': breach.get('AddedDate'),
                            'modified_date': breach.get('ModifiedDate'),
                            'pwn_count': breach.get('PwnCount'),
                            'description': breach.get('Description'),
                            'data_classes': breach.get('DataClasses', []),
                            'is_verified': breach.get('IsVerified'),
                            'is_fabricated': breach.get('IsFabricated'),
                            'is_sensitive': breach.get('IsSensitive'),
                            'is_retired': breach.get('IsRetired'),
                            'is_spam_list': breach.get('IsSpamList')
                        })
                    
                    return breaches
                
                elif response.status == 404:
                    # No breaches found
                    return []
                else:
                    # API error
                    return []
    
    async def _check_pastes(self) -> list:
        """Check for pastes"""
        url = f"https://haveibeenpwned.com/api/v3/pasteaccount/{self.target}"
        
        headers = {
            'hibp-api-key': self.api_key,
            'user-agent': 'PHINEAS-OSINT'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        pastes = []
                        for paste in data:
                            pastes.append({
                                'source': paste.get('Source'),
                                'id': paste.get('Id'),
                                'title': paste.get('Title'),
                                'date': paste.get('Date'),
                                'email_count': paste.get('EmailCount')
                            })
                        
                        return pastes
                    else:
                        return []
        except Exception:
            return []


# Standalone execution
if __name__ == '__main__':
    import asyncio
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python hibp_plugin.py <email>")
        print("Set PHINEAS_HAVEIBEENPWNED_API_KEY environment variable")
        sys.exit(1)
    
    api_key = os.getenv('PHINEAS_HAVEIBEENPWNED_API_KEY')
    if not api_key:
        print("Error: PHINEAS_HAVEIBEENPWNED_API_KEY not set")
        sys.exit(1)
    
    plugin = Plugin(target=sys.argv[1], api_keys={'haveibeenpwned': api_key})
    result = asyncio.run(plugin.run())
    
    import json
    print(json.dumps(result, indent=2))
