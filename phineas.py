#!/usr/bin/env python3
"""
PHINEAS CLI - Command Line Interface
Main entry point for PHINEAS OSINT Framework
"""

import asyncio
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import PhineasOrchestrator
from core.config_manager import ConfigManager
from core.result_aggregator import ResultAggregator

console = Console()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    PHINEAS - Profound HUMINT Intelligence Network & Enrichment Automated System
    
    Comprehensive OSINT automation framework
    """
    pass


@cli.command()
@click.option('--target', required=True, help='Target identifier (email, username, domain)')
@click.option('--workflow', default='auto', help='Workflow to execute (auto, email_intelligence, domain_reconnaissance, username_enumeration)')
@click.option('--config', type=click.Path(), help='Custom config file')
@click.option('--output', type=click.Path(), help='Output directory')
def scan(target, workflow, config, output):
    """Run an OSINT scan on a target"""
    console.print(f"\n[bold cyan]PHINEAS OSINT Scan[/bold cyan]\n")
    
    config_path = Path(config) if config else None
    orchestrator = PhineasOrchestrator(config_path=config_path)
    
    if output:
        orchestrator.config['output_dir'] = output
    
    # Auto-detect workflow
    if workflow == 'auto':
        if '@' in target:
            workflow = 'email_intelligence'
            console.print(f"[yellow]Auto-detected:[/yellow] Email Intelligence workflow")
        elif '.' in target and len(target.split('.')) >= 2:
            workflow = 'domain_reconnaissance'
            console.print(f"[yellow]Auto-detected:[/yellow] Domain Reconnaissance workflow")
        else:
            workflow = 'username_enumeration'
            console.print(f"[yellow]Auto-detected:[/yellow] Username Enumeration workflow")
    
    workflow_file = Path(__file__).parent / 'workflows' / f'{workflow}.yaml'
    
    if not workflow_file.exists():
        console.print(f"[red]Workflow not found:[/red] {workflow}")
        sys.exit(1)
    
    import yaml
    with open(workflow_file) as f:
        workflow_def = yaml.safe_load(f)
    
    # Execute
    result = asyncio.run(orchestrator.execute_workflow(workflow_def, target))
    
    console.print(f"\n[green]Scan complete![/green]")


@cli.command()
def setup():
    """Interactive setup and configuration"""
    config_manager = ConfigManager()
    config_manager.interactive_setup()


@cli.command()
@click.argument('service')
@click.argument('key')
@click.option('--storage', type=click.Choice(['keyring', 'env', 'config']), default='keyring')
def setkey(service, key, storage):
    """Set API key for a service"""
    config_manager = ConfigManager()
    config_manager.set_api_key(service, key, storage)
    console.print(f"[green]OK[/green] API key for {service} configured")


@cli.command()
def keys():
    """List configured API keys"""
    config_manager = ConfigManager()
    status = config_manager.list_api_keys()
    
    table = Table(title="API Key Status", show_header=True, header_style="bold cyan")
    table.add_column("Service", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Description")
    
    descriptions = {
        'shodan': 'Internet-connected device search',
        'haveibeenpwned': 'Data breach checking',
        'securitytrails': 'Historical DNS data',
        'virustotal': 'File/URL scanning',
        'hunter': 'Email finder and verifier',
        'snusbase': 'Dark web credentials',
        'dehashed': 'Data breach search',
        'censys': 'Internet-wide scanning',
        'github': 'GitHub API access',
        'twitter': 'Twitter API access',
        'numverify': 'Phone number validation',
        'clearbit': 'Company data enrichment'
    }
    
    for service, configured in status.items():
        status_icon = "[OK]" if configured else "[X]"
        status_color = "green" if configured else "red"
        status_text = f"[{status_color}]{status_icon} {'Configured' if configured else 'Not configured'}[/{status_color}]"
        description = descriptions.get(service, '')
        
        table.add_row(service, status_text, description)
    
    console.print("\n")
    console.print(table)
    console.print("\n[dim]Use 'phineas setkey <service> <key>' to configure[/dim]")


@cli.command()
def plugins():
    """List available OSINT plugins"""
    table = Table(title="Available PHINEAS Plugins", show_header=True, header_style="bold cyan")
    table.add_column("Plugin", style="yellow")
    table.add_column("Category", style="cyan")
    table.add_column("API Key", style="magenta")
    table.add_column("Description")
    
    plugins_info = [
        ('sherlock', 'People', 'No', 'Username enumeration across 300+ sites'),
        ('holehe', 'Email', 'No', 'Email to account finder'),
        ('theharvester', 'Email/Domain', 'No', 'Email and subdomain harvesting'),
        ('haveibeenpwned', 'Breach', 'Yes', 'Data breach checking'),
        ('sublist3r', 'Domain', 'No', 'Subdomain enumeration'),
        ('wayback', 'Passive', 'No', 'Historical website data'),
        ('maigret', 'People', 'No', 'Enhanced username search (2500+ sites)'),
        ('phoneinfoga', 'Phone', 'No', 'Phone number OSINT'),
        ('shodan', 'Domain', 'Yes', 'Internet-connected device search'),
        ('amass', 'Domain', 'No', 'In-depth DNS enumeration'),
    ]
    
    for name, category, api_key, description in plugins_info:
        table.add_row(name, category, api_key, description)
    
    console.print("\n")
    console.print(table)


@cli.command()
def workflows():
    """List available workflows"""
    console.print("\n[bold cyan]📋 Available Workflows[/bold cyan]\n")
    
    workflows_info = [
        {
            'name': 'email_intelligence',
            'target': 'Email address',
            'plugins': ['holehe', 'haveibeenpwned', 'sherlock', 'theharvester'],
            'description': 'Comprehensive email reconnaissance and breach checking'
        },
        {
            'name': 'domain_reconnaissance',
            'target': 'Domain name',
            'plugins': ['sublist3r', 'theharvester', 'wayback'],
            'description': 'Full spectrum domain reconnaissance and attack surface mapping'
        },
        {
            'name': 'username_enumeration',
            'target': 'Username',
            'plugins': ['sherlock', 'holehe'],
            'description': 'Track digital footprint across social media platforms'
        }
    ]
    
    for wf in workflows_info:
        console.print(f"[yellow]- {wf['name']}[/yellow]")
        console.print(f"  Target: {wf['target']}")
        console.print(f"  Plugins: {', '.join(wf['plugins'])}")
        console.print(f"  {wf['description']}\n")


@cli.command()
def install():
    """Install OSINT tools and dependencies"""
    console.print("\n[bold cyan]📦 PHINEAS Tool Installation[/bold cyan]\n")
    console.print("[yellow]Installing OSINT tools...[/yellow]\n")
    
    tools = [
        ('sherlock', 'pip install sherlock-project'),
        ('holehe', 'pip install holehe'),
        ('theHarvester', 'pip install theHarvester'),
        ('sublist3r', 'pip install sublist3r'),
    ]
    
    import subprocess
    
    for tool_name, install_cmd in tools:
        console.print(f"[cyan]Installing {tool_name}...[/cyan]")
        try:
            result = subprocess.run(
                install_cmd.split(),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                console.print(f"  [green]OK {tool_name} installed[/green]")
            else:
                console.print(f"  [red]FAIL {tool_name} failed[/red]")
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")
    
    console.print("\n[green]Installation complete![/green]")


@cli.command()
@click.option('--client', required=True, help='Cronos client name')
@click.option('--scan-id', type=int, help='Specific scan ID (uses latest if omitted)')
def cronos(client, scan_id):
    """[OPTIONAL] Enrich Cronos scan with PHINEAS OSINT"""
    from integrations.cronos_bridge import CronosBridge
    
    console.print(f"\n[bold cyan]PHINEAS x Cronos Integration[/bold cyan]\n")
    console.print("[yellow]Note: This is an optional integration feature[/yellow]\n")
    
    bridge = CronosBridge()
    asyncio.run(bridge.enrich_client_scan(client, scan_id))


if __name__ == '__main__':
    cli()
