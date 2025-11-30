#!/usr/bin/env python3
"""
PHINEAS Result Aggregator
Normalizes and aggregates results from multiple OSINT plugins
"""

from typing import Dict, List, Any, Set
from collections import defaultdict
import json
from datetime import datetime


class ResultAggregator:
    """
    Aggregates and normalizes results from multiple OSINT sources
    
    Handles:
    - Deduplication
    - Data normalization
    - Confidence scoring
    - Relationship mapping
    """
    
    def __init__(self):
        self.raw_results = []
        self.aggregated = {
            'emails': set(),
            'usernames': set(),
            'domains': set(),
            'subdomains': set(),
            'phone_numbers': set(),
            'urls': set(),
            'social_profiles': [],
            'breaches': [],
            'accounts': [],
            'metadata': {}
        }
        self.sources = defaultdict(list)
    
    def add_result(self, plugin_name: str, result: Dict):
        """Add a plugin result to the aggregator"""
        self.raw_results.append({
            'plugin': plugin_name,
            'timestamp': datetime.now().isoformat(),
            'result': result
        })
        
        # Extract structured data
        findings = result.get('findings', {})
        
        # Emails
        if 'emails' in findings:
            emails = findings['emails'] if isinstance(findings['emails'], list) else [findings['emails']]
            for email in emails:
                self.aggregated['emails'].add(email.lower().strip())
                self.sources[f'email:{email}'].append(plugin_name)
        
        # Usernames
        if 'usernames' in findings:
            usernames = findings['usernames'] if isinstance(findings['usernames'], list) else [findings['usernames']]
            for username in usernames:
                self.aggregated['usernames'].add(username.strip())
                self.sources[f'username:{username}'].append(plugin_name)
        
        # Domains
        if 'domains' in findings:
            domains = findings['domains'] if isinstance(findings['domains'], list) else [findings['domains']]
            for domain in domains:
                self.aggregated['domains'].add(domain.lower().strip())
                self.sources[f'domain:{domain}'].append(plugin_name)
        
        # Subdomains
        if 'subdomains' in findings:
            subdomains = findings['subdomains'] if isinstance(findings['subdomains'], list) else [findings['subdomains']]
            for subdomain in subdomains:
                self.aggregated['subdomains'].add(subdomain.lower().strip())
                self.sources[f'subdomain:{subdomain}'].append(plugin_name)
        
        # Phone numbers
        if 'phone_numbers' in findings:
            phones = findings['phone_numbers'] if isinstance(findings['phone_numbers'], list) else [findings['phone_numbers']]
            for phone in phones:
                self.aggregated['phone_numbers'].add(phone.strip())
                self.sources[f'phone:{phone}'].append(plugin_name)
        
        # URLs
        if 'urls' in findings:
            urls = findings['urls'] if isinstance(findings['urls'], list) else [findings['urls']]
            for url in urls:
                self.aggregated['urls'].add(url.strip())
        
        # Social profiles
        if 'social_profiles' in findings:
            profiles = findings['social_profiles'] if isinstance(findings['social_profiles'], list) else [findings['social_profiles']]
            for profile in profiles:
                if isinstance(profile, dict):
                    profile['source'] = plugin_name
                    self.aggregated['social_profiles'].append(profile)
        
        # Accounts
        if 'accounts' in findings:
            accounts = findings['accounts'] if isinstance(findings['accounts'], list) else [findings['accounts']]
            for account in accounts:
                if isinstance(account, dict):
                    account['source'] = plugin_name
                    self.aggregated['accounts'].append(account)
                elif isinstance(account, str):
                    self.aggregated['accounts'].append({
                        'platform': 'unknown',
                        'account': account,
                        'source': plugin_name
                    })
        
        # Breaches
        if 'breaches' in findings:
            breaches = findings['breaches'] if isinstance(findings['breaches'], list) else [findings['breaches']]
            for breach in breaches:
                if isinstance(breach, dict):
                    breach['source'] = plugin_name
                    self.aggregated['breaches'].append(breach)
    
    def get_aggregated_results(self) -> Dict:
        """Get aggregated and deduplicated results"""
        results = {
            'summary': {
                'total_emails': len(self.aggregated['emails']),
                'total_usernames': len(self.aggregated['usernames']),
                'total_domains': len(self.aggregated['domains']),
                'total_subdomains': len(self.aggregated['subdomains']),
                'total_phone_numbers': len(self.aggregated['phone_numbers']),
                'total_urls': len(self.aggregated['urls']),
                'total_social_profiles': len(self.aggregated['social_profiles']),
                'total_accounts': len(self.aggregated['accounts']),
                'total_breaches': len(self.aggregated['breaches']),
            },
            'data': {
                'emails': sorted(list(self.aggregated['emails'])),
                'usernames': sorted(list(self.aggregated['usernames'])),
                'domains': sorted(list(self.aggregated['domains'])),
                'subdomains': sorted(list(self.aggregated['subdomains'])),
                'phone_numbers': sorted(list(self.aggregated['phone_numbers'])),
                'urls': sorted(list(self.aggregated['urls'])),
                'social_profiles': self._deduplicate_profiles(self.aggregated['social_profiles']),
                'accounts': self._deduplicate_accounts(self.aggregated['accounts']),
                'breaches': self.aggregated['breaches'],
            },
            'confidence': self._calculate_confidence(),
            'sources': {k: v for k, v in self.sources.items()}
        }
        
        return results
    
    def _deduplicate_profiles(self, profiles: List[Dict]) -> List[Dict]:
        """Deduplicate social media profiles"""
        seen = set()
        unique = []
        
        for profile in profiles:
            key = f"{profile.get('platform', 'unknown')}:{profile.get('url', profile.get('username', ''))}"
            if key not in seen:
                seen.add(key)
                unique.append(profile)
        
        return unique
    
    def _deduplicate_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """Deduplicate accounts"""
        seen = set()
        unique = []
        
        for account in accounts:
            key = f"{account.get('platform', 'unknown')}:{account.get('account', account.get('email', ''))}"
            if key not in seen:
                seen.add(key)
                unique.append(account)
        
        return unique
    
    def _calculate_confidence(self) -> Dict[str, int]:
        """
        Calculate confidence scores for findings
        
        Higher confidence when multiple sources report the same finding
        """
        confidence = {}
        
        for key, sources in self.sources.items():
            source_count = len(set(sources))
            
            if source_count >= 3:
                confidence[key] = 100
            elif source_count == 2:
                confidence[key] = 75
            else:
                confidence[key] = 50
        
        return confidence
    
    def export_json(self, output_path: str):
        """Export aggregated results to JSON"""
        results = self.get_aggregated_results()
        
        # Convert sets to lists for JSON serialization
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def export_csv(self, output_path: str, data_type: str = 'all'):
        """Export specific data type to CSV"""
        import csv
        
        results = self.get_aggregated_results()
        
        with open(output_path, 'w', newline='') as f:
            if data_type == 'emails':
                writer = csv.writer(f)
                writer.writerow(['Email', 'Sources', 'Confidence'])
                for email in results['data']['emails']:
                    key = f'email:{email}'
                    sources = ', '.join(self.sources.get(key, ['unknown']))
                    confidence = results['confidence'].get(key, 50)
                    writer.writerow([email, sources, confidence])
            
            elif data_type == 'social_profiles':
                writer = csv.DictWriter(f, fieldnames=['platform', 'username', 'url', 'source'])
                writer.writeheader()
                for profile in results['data']['social_profiles']:
                    writer.writerow(profile)
            
            elif data_type == 'breaches':
                if results['data']['breaches']:
                    fieldnames = list(results['data']['breaches'][0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for breach in results['data']['breaches']:
                        writer.writerow(breach)
