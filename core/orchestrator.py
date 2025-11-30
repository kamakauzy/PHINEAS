#!/usr/bin/env python3
"""
PHINEAS Core Orchestrator
Manages OSINT workflow execution and plugin coordination
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import yaml

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel

console = Console()
logger = logging.getLogger(__name__)


class PhineasOrchestrator:
    """
    Central orchestration engine for PHINEAS OSINT workflows
    
    Coordinates plugin execution, manages dependencies, aggregates results
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "phineas.yaml"
        self.config = self._load_config()
        self.plugins = {}
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def _load_config(self) -> Dict:
        """Load PHINEAS configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'output_dir': './phineas-results',
            'concurrent_scans': 5,
            'timeout': 300,
            'retry_failed': True,
            'max_retries': 2,
            'api_keys': {},
            'enabled_plugins': []
        }
    
    def register_plugin(self, plugin_name: str, plugin_class):
        """Register an OSINT plugin"""
        self.plugins[plugin_name] = plugin_class
        logger.info(f"Registered plugin: {plugin_name}")
    
    async def execute_workflow(self, workflow: Dict, target: str) -> Dict:
        """
        Execute an OSINT workflow
        
        Args:
            workflow: Workflow definition (YAML loaded dict)
            target: Target identifier (email, username, domain, etc.)
            
        Returns:
            Aggregated results dictionary
        """
        self.start_time = datetime.now()
        
        console.print(Panel.fit(
            f"[bold cyan]PHINEAS OSINT Workflow[/bold cyan]\n"
            f"[white]Target:[/white] [yellow]{target}[/yellow]\n"
            f"[white]Workflow:[/white] {workflow.get('name', 'custom')}\n"
            f"[white]Steps:[/white] {len(workflow.get('steps', []))} plugins",
            title="Starting Reconnaissance",
            border_style="cyan"
        ))
        
        results = {
            'target': target,
            'workflow': workflow.get('name', 'custom'),
            'start_time': self.start_time.isoformat(),
            'plugins': {},
            'summary': {}
        }
        
        # Execute workflow steps
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            total_steps = len(workflow.get('steps', []))
            main_task = progress.add_task("[cyan]Overall progress...", total=total_steps)
            
            for step in workflow.get('steps', []):
                plugin_name = step if isinstance(step, str) else step.get('name')
                plugin_config = step if isinstance(step, dict) else {}
                
                try:
                    progress.update(main_task, description=f"[cyan]Running {plugin_name}...")
                    
                    plugin_result = await self._run_plugin(
                        plugin_name,
                        target,
                        plugin_config
                    )
                    results['plugins'][plugin_name] = plugin_result
                    
                    status_icon = "OK" if plugin_result.get('status') == 'success' else "WARN"
                    console.print(f"{status_icon} [green]{plugin_name}[/green] completed")
                    
                except Exception as e:
                    logger.error(f"Plugin {plugin_name} failed: {e}")
                    results['plugins'][plugin_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    console.print(f"FAIL [red]{plugin_name}[/red] failed: {str(e)}")
                
                progress.update(main_task, advance=1)
        
        self.end_time = datetime.now()
        results['end_time'] = self.end_time.isoformat()
        results['duration_seconds'] = (self.end_time - self.start_time).total_seconds()
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        # Save results
        self._save_results(results)
        
        # Display summary
        self._display_summary(results)
        
        return results
    
    async def _run_plugin(self, plugin_name: str, target: str, config: Dict) -> Dict:
        """Execute a single plugin"""
        if plugin_name not in self.plugins:
            # Try to dynamically import
            try:
                plugin_class = self._import_plugin(plugin_name)
                self.plugins[plugin_name] = plugin_class
            except ImportError as e:
                raise ValueError(f"Plugin {plugin_name} not found: {e}")
        
        plugin_class = self.plugins[plugin_name]
        
        # Merge plugin config with global config
        plugin_config = {
            **self.config.get('plugins', {}).get(plugin_name, {}),
            **config
        }
        
        # Initialize and run plugin
        plugin = plugin_class(
            target=target,
            config=plugin_config,
            api_keys=self.config.get('api_keys', {})
        )
        
        result = await plugin.run()
        return result
    
    def _import_plugin(self, plugin_name: str):
        """Dynamically import a plugin class"""
        # Determine plugin category
        plugin_map = {
            'sherlock': 'plugins.people.sherlock_plugin',
            'holehe': 'plugins.email.holehe_plugin',
            'theharvester': 'plugins.email.harvester_plugin',
            'phoneinfoga': 'plugins.phone.phoneinfoga_plugin',
            'sublist3r': 'plugins.domain.sublist3r_plugin',
            'subfinder': 'plugins.domain.subfinder_plugin',
            'shodan': 'plugins.domain.shodan_plugin',
            'haveibeenpwned': 'plugins.breach.hibp_plugin',
            'ghunt': 'plugins.people.ghunt_plugin',
            'maigret': 'plugins.people.maigret_plugin',
            'blackbird': 'plugins.people.blackbird_plugin',
            'amass': 'plugins.domain.amass_plugin',
            'wayback': 'plugins.passive.wayback_plugin',
            'email_validator': 'plugins.email.validator_plugin',
        }
        
        module_path = plugin_map.get(plugin_name)
        if not module_path:
            raise ImportError(f"Unknown plugin: {plugin_name}")
        
        module = __import__(f"phineas.{module_path}", fromlist=['Plugin'])
        return module.Plugin
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate summary statistics from results"""
        summary = {
            'total_plugins': len(results['plugins']),
            'successful': 0,
            'failed': 0,
            'findings': {},
            'highlights': []
        }
        
        for plugin_name, plugin_result in results['plugins'].items():
            if plugin_result.get('status') == 'success':
                summary['successful'] += 1
                
                # Aggregate findings
                findings = plugin_result.get('findings', {})
                for key, value in findings.items():
                    if key not in summary['findings']:
                        summary['findings'][key] = []
                    if isinstance(value, list):
                        summary['findings'][key].extend(value)
                    else:
                        summary['findings'][key].append(value)
            else:
                summary['failed'] += 1
        
        # Generate highlights
        if summary['findings'].get('emails'):
            unique_emails = len(set(summary['findings']['emails']))
            summary['highlights'].append(
                f"{unique_emails} unique email(s) discovered"
            )
        if summary['findings'].get('usernames'):
            unique_usernames = len(set(summary['findings']['usernames']))
            summary['highlights'].append(
                f"{unique_usernames} social media profile(s) found"
            )
        if summary['findings'].get('subdomains'):
            unique_subdomains = len(set(summary['findings']['subdomains']))
            summary['highlights'].append(
                f"{unique_subdomains} subdomain(s) enumerated"
            )
        if summary['findings'].get('breaches'):
            summary['highlights'].append(
                f"{len(summary['findings']['breaches'])} data breach(es) identified"
            )
        if summary['findings'].get('accounts'):
            unique_accounts = len(set(summary['findings']['accounts']))
            summary['highlights'].append(
                f"{unique_accounts} online account(s) discovered"
            )
        
        return summary
    
    def _save_results(self, results: Dict):
        """Save results to disk"""
        output_dir = Path(self.config.get('output_dir', './phineas-results'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        target_safe = results['target'].replace('@', '_at_').replace('.', '_').replace('/', '_')
        
        output_file = output_dir / f"phineas_{target_safe}_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {output_file}")
        console.print(f"\n[green]Results saved:[/green] {output_file}")
    
    def _display_summary(self, results: Dict):
        """Display results summary in terminal"""
        summary = results['summary']
        
        # Summary table
        table = Table(title="🎯 PHINEAS Results Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="yellow")
        table.add_column("Value", style="green")
        
        table.add_row("Target", results['target'])
        table.add_row("Workflow", results['workflow'])
        table.add_row("Duration", f"{results['duration_seconds']:.2f}s")
        table.add_row("Total Plugins", str(summary['total_plugins']))
        table.add_row("Successful", str(summary['successful']))
        table.add_row("Failed", str(summary['failed']))
        
        console.print("\n")
        console.print(table)
        
        # Highlights
        if summary['highlights']:
            console.print("\n[bold cyan]Key Findings:[/bold cyan]")
            for highlight in summary['highlights']:
                console.print(f"  - {highlight}")
        
        console.print("\n[bold green]PHINEAS reconnaissance complete![/bold green]")


async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PHINEAS - Profound HUMINT Intelligence Network & Enrichment Automated System"
    )
    parser.add_argument('--target', required=True, help='Target identifier (email, username, domain)')
    parser.add_argument('--workflow', default='auto', help='Workflow to execute')
    parser.add_argument('--config', type=Path, help='Custom config file')
    
    args = parser.parse_args()
    
    orchestrator = PhineasOrchestrator(config_path=args.config)
    
    # Load workflow
    if args.workflow == 'auto':
        # Auto-detect workflow based on target
        if '@' in args.target:
            workflow_name = 'email_intelligence'
        elif '.' in args.target and len(args.target.split('.')) >= 2:
            workflow_name = 'domain_reconnaissance'
        else:
            workflow_name = 'username_enumeration'
    else:
        workflow_name = args.workflow
    
    workflow_file = Path(__file__).parent.parent / 'workflows' / f'{workflow_name}.yaml'
    
    if workflow_file.exists():
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)
    else:
        console.print(f"[red]Workflow not found: {workflow_name}[/red]")
        return
    
    # Execute
    await orchestrator.execute_workflow(workflow, args.target)


if __name__ == '__main__':
    asyncio.run(main())
