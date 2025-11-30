#!/usr/bin/env python3
"""
PHINEAS Cronos Integration Bridge
Seamlessly integrates PHINEAS OSINT into Cronos scanning platform
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import PhineasOrchestrator
from core.config_manager import ConfigManager
from core.result_aggregator import ResultAggregator


class CronosBridge:
    """
    Bridge between PHINEAS and Cronos platforms
    
    Features:
    - Automatic enrichment of Cronos scan results
    - PostgreSQL database integration
    - Email/domain/subdomain OSINT enrichment
    - Breach intelligence injection
    """
    
    def __init__(self, cronos_db_config: Dict = None):
        self.config_manager = ConfigManager()
        self.orchestrator = PhineasOrchestrator()
        self.db_config = cronos_db_config or self._get_cronos_db_config()
        self.db_conn = None
        
    def _get_cronos_db_config(self) -> Dict:
        """Get Cronos database configuration"""
        cronos_config = self.config_manager.config.get('integrations', {}).get('cronos', {})
        
        return {
            'host': cronos_config.get('db_host', 'localhost'),
            'port': cronos_config.get('db_port', 5432),
            'database': cronos_config.get('db_name', 'cronos'),
            'user': cronos_config.get('db_user', 'postgres'),
            'password': cronos_config.get('db_password', '')
        }
    
    async def connect_database(self):
        """Connect to Cronos PostgreSQL database"""
        try:
            import psycopg2
            
            self.db_conn = psycopg2.connect(**self.db_config)
            print(f"✓ Connected to Cronos database: {self.db_config['database']}")
        except ImportError:
            print("⚠ psycopg2 not installed. Database integration unavailable.")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
    
    async def enrich_client_scan(self, client_name: str, scan_id: Optional[int] = None):
        """
        Enrich Cronos scan results with PHINEAS OSINT
        
        Args:
            client_name: Client identifier
            scan_id: Optional specific scan ID (uses latest if None)
        """
        if not self.db_conn:
            await self.connect_database()
        
        print(f"\n🔍 PHINEAS Enrichment for Cronos Client: {client_name}")
        print("=" * 60)
        
        # Get scan data from Cronos
        scan_data = await self._get_scan_data(client_name, scan_id)
        
        if not scan_data:
            print("✗ No scan data found")
            return
        
        # Extract targets for OSINT
        targets = self._extract_targets(scan_data)
        
        print(f"\n📊 Found {len(targets['emails'])} emails, {len(targets['domains'])} domains")
        
        # Run OSINT workflows
        osint_results = await self._run_osint_workflows(targets)
        
        # Inject results back into Cronos
        await self._inject_results(client_name, scan_id, osint_results)
        
        print("\n✓ PHINEAS enrichment complete!")
    
    async def _get_scan_data(self, client_name: str, scan_id: Optional[int]) -> Dict:
        """Retrieve scan data from Cronos database"""
        if not self.db_conn:
            return {}
        
        cursor = self.db_conn.cursor()
        
        try:
            # Get client ID
            cursor.execute(
                "SELECT client_id FROM clients WHERE client_name = %s",
                (client_name,)
            )
            result = cursor.fetchone()
            
            if not result:
                print(f"✗ Client not found: {client_name}")
                return {}
            
            client_id = result[0]
            
            # Get scan data
            if scan_id:
                query = """
                    SELECT scan_id, scan_timestamp, scan_directory
                    FROM scans
                    WHERE client_id = %s AND scan_id = %s
                """
                cursor.execute(query, (client_id, scan_id))
            else:
                query = """
                    SELECT scan_id, scan_timestamp, scan_directory
                    FROM scans
                    WHERE client_id = %s
                    ORDER BY scan_timestamp DESC
                    LIMIT 1
                """
                cursor.execute(query, (client_id,))
            
            result = cursor.fetchone()
            
            if not result:
                return {}
            
            scan_id, scan_timestamp, scan_directory = result
            
            return {
                'client_id': client_id,
                'scan_id': scan_id,
                'scan_timestamp': scan_timestamp,
                'scan_directory': scan_directory
            }
        
        finally:
            cursor.close()
    
    def _extract_targets(self, scan_data: Dict) -> Dict:
        """Extract OSINT targets from Cronos scan data"""
        targets = {
            'emails': set(),
            'domains': set(),
            'subdomains': set(),
            'ips': set()
        }
        
        if not self.db_conn or not scan_data:
            return targets
        
        cursor = self.db_conn.cursor()
        scan_id = scan_data['scan_id']
        
        try:
            # Extract emails from findings
            cursor.execute("""
                SELECT DISTINCT email
                FROM emails
                WHERE scan_id = %s
            """, (scan_id,))
            
            for row in cursor.fetchall():
                if row[0]:
                    targets['emails'].add(row[0])
            
            # Extract subdomains
            cursor.execute("""
                SELECT DISTINCT subdomain
                FROM subdomains
                WHERE scan_id = %s
            """, (scan_id,))
            
            for row in cursor.fetchall():
                if row[0]:
                    targets['subdomains'].add(row[0])
            
            # Extract domains from subdomains
            for subdomain in targets['subdomains']:
                parts = subdomain.split('.')
                if len(parts) >= 2:
                    domain = '.'.join(parts[-2:])
                    targets['domains'].add(domain)
        
        finally:
            cursor.close()
        
        # Convert to lists
        return {
            'emails': list(targets['emails']),
            'domains': list(targets['domains']),
            'subdomains': list(targets['subdomains']),
            'ips': list(targets['ips'])
        }
    
    async def _run_osint_workflows(self, targets: Dict) -> Dict:
        """Run appropriate OSINT workflows for targets"""
        results = {
            'emails': {},
            'domains': {},
            'aggregated': ResultAggregator()
        }
        
        # Email intelligence
        for email in targets['emails'][:10]:  # Limit to first 10
            print(f"\n  → Running email intelligence: {email}")
            try:
                workflow_file = Path(__file__).parent.parent / 'workflows' / 'email_intelligence.yaml'
                
                if workflow_file.exists():
                    import yaml
                    with open(workflow_file) as f:
                        workflow = yaml.safe_load(f)
                    
                    result = await self.orchestrator.execute_workflow(workflow, email)
                    results['emails'][email] = result
                    
                    # Add to aggregator
                    for plugin_name, plugin_result in result['plugins'].items():
                        results['aggregated'].add_result(plugin_name, plugin_result)
            except Exception as e:
                print(f"    ✗ Failed: {e}")
        
        # Domain reconnaissance
        for domain in targets['domains'][:5]:  # Limit to first 5
            print(f"\n  → Running domain reconnaissance: {domain}")
            try:
                workflow_file = Path(__file__).parent.parent / 'workflows' / 'domain_reconnaissance.yaml'
                
                if workflow_file.exists():
                    import yaml
                    with open(workflow_file) as f:
                        workflow = yaml.safe_load(f)
                    
                    result = await self.orchestrator.execute_workflow(workflow, domain)
                    results['domains'][domain] = result
                    
                    # Add to aggregator
                    for plugin_name, plugin_result in result['plugins'].items():
                        results['aggregated'].add_result(plugin_name, plugin_result)
            except Exception as e:
                print(f"    ✗ Failed: {e}")
        
        return results
    
    async def _inject_results(self, client_name: str, scan_id: Optional[int], osint_results: Dict):
        """Inject PHINEAS results back into Cronos database"""
        if not self.db_conn:
            print("⚠ Database not connected, skipping injection")
            return
        
        cursor = self.db_conn.cursor()
        aggregated = osint_results['aggregated'].get_aggregated_results()
        
        try:
            # Insert breach data
            for email, result in osint_results['emails'].items():
                breaches = result.get('plugins', {}).get('haveibeenpwned', {}).get('findings', {}).get('breaches', [])
                
                for breach in breaches:
                    cursor.execute("""
                        INSERT INTO darkweb_credentials 
                        (scan_id, email, breach_name, breach_date, breach_source, raw_snusbase_data)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        scan_id,
                        email,
                        breach.get('name'),
                        breach.get('breach_date'),
                        'haveibeenpwned',
                        json.dumps(breach)
                    ))
            
            # Insert discovered subdomains
            for subdomain in aggregated['data']['subdomains']:
                cursor.execute("""
                    INSERT INTO subdomains (scan_id, subdomain, discovered_by)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (scan_id, subdomain, 'phineas_osint'))
            
            # Insert social profiles
            for profile in aggregated['data']['social_profiles']:
                cursor.execute("""
                    INSERT INTO osint_findings 
                    (scan_id, finding_type, platform, username, url, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    scan_id,
                    'social_profile',
                    profile.get('platform'),
                    profile.get('username'),
                    profile.get('url'),
                    json.dumps(profile)
                ))
            
            self.db_conn.commit()
            print(f"\n✓ Injected {len(aggregated['data']['breaches'])} breaches")
            print(f"✓ Injected {len(aggregated['data']['subdomains'])} subdomains")
            print(f"✓ Injected {len(aggregated['data']['social_profiles'])} social profiles")
        
        except Exception as e:
            print(f"✗ Injection error: {e}")
            self.db_conn.rollback()
        finally:
            cursor.close()


async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PHINEAS Cronos Integration Bridge"
    )
    
    parser.add_argument('--client', required=True, help='Client name')
    parser.add_argument('--scan-id', type=int, help='Specific scan ID (uses latest if omitted)')
    parser.add_argument('--db-host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--db-port', default=5432, type=int, help='PostgreSQL port')
    parser.add_argument('--db-name', default='cronos', help='Database name')
    parser.add_argument('--db-user', default='postgres', help='Database user')
    parser.add_argument('--db-password', help='Database password')
    
    args = parser.parse_args()
    
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password or ''
    }
    
    bridge = CronosBridge(cronos_db_config=db_config)
    await bridge.enrich_client_scan(args.client, args.scan_id)


if __name__ == '__main__':
    asyncio.run(main())
