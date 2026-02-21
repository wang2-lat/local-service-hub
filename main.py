import typer
from rich.console import Console
from rich.table import Table
from database import Database
from datetime import datetime

app = typer.Typer(help="Local Service Hub - Manage leads and contractor network")
console = Console()
db = Database()

@app.command()
def provider_add(
    name: str = typer.Option(..., prompt=True),
    service_type: str = typer.Option(..., prompt=True, help="e.g., plumbing, electrical, cleaning"),
    coverage_area: str = typer.Option(..., prompt=True, help="e.g., Downtown, North Side"),
    contact: str = typer.Option(..., prompt=True, help="Phone or email")
):
    """Add a new service provider"""
    provider_id = db.add_provider(name, service_type, coverage_area, contact)
    console.print(f"[green]✓[/green] Provider added with ID: {provider_id}")

@app.command()
def provider_list(service_type: str = typer.Option(None, help="Filter by service type")):
    """List all service providers"""
    providers = db.get_providers(service_type)
    
    if not providers:
        console.print("[yellow]No providers found[/yellow]")
        return
    
    table = Table(title="Service Providers")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Service Type", style="magenta")
    table.add_column("Coverage Area", style="blue")
    table.add_column("Contact", style="yellow")
    table.add_column("Reliability", style="red")
    
    for p in providers:
        table.add_row(str(p[0]), p[1], p[2], p[3], p[4], f"{p[5]}/10")
    
    console.print(table)

@app.command()
def provider_rate(
    provider_id: int = typer.Argument(..., help="Provider ID"),
    score: int = typer.Argument(..., help="Reliability score (1-10)")
):
    """Update provider reliability score"""
    if score < 1 or score > 10:
        console.print("[red]Score must be between 1 and 10[/red]")
        return
    
    db.update_provider_reliability(provider_id, score)
    console.print(f"[green]✓[/green] Provider {provider_id} reliability updated to {score}/10")

@app.command()
def lead_add(
    service_type: str = typer.Option(..., prompt=True, help="Required service type"),
    location: str = typer.Option(..., prompt=True, help="Service location"),
    description: str = typer.Option(..., prompt=True, help="Job description")
):
    """Add a new customer lead"""
    lead_id = db.add_lead(service_type, location, description)
    console.print(f"[green]✓[/green] Lead added with ID: {lead_id}")
    
    # Auto-match
    matches = db.match_lead(lead_id)
    if matches:
        console.print(f"\n[cyan]Found {len(matches)} matching providers:[/cyan]")
        for match in matches:
            console.print(f"  • {match[1]} (Reliability: {match[2]}/10) - {match[3]}")
    else:
        console.print("[yellow]No matching providers found[/yellow]")

@app.command()
def lead_list(status: str = typer.Option("pending", help="Filter by status: pending, matched, closed")):
    """List customer leads"""
    leads = db.get_leads(status)
    
    if not leads:
        console.print(f"[yellow]No {status} leads found[/yellow]")
        return
    
    table = Table(title=f"{status.capitalize()} Leads")
    table.add_column("ID", style="cyan")
    table.add_column("Service Type", style="magenta")
    table.add_column("Location", style="blue")
    table.add_column("Description", style="white")
    table.add_column("Created", style="yellow")
    
    for lead in leads:
        table.add_row(str(lead[0]), lead[1], lead[2], lead[3][:50], lead[5])
    
    console.print(table)

@app.command()
def lead_match(lead_id: int = typer.Argument(..., help="Lead ID")):
    """Find matching providers for a lead"""
    matches = db.match_lead(lead_id)
    
    if not matches:
        console.print("[yellow]No matching providers found[/yellow]")
        return
    
    table = Table(title=f"Matches for Lead #{lead_id}")
    table.add_column("Provider ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Reliability", style="red")
    table.add_column("Contact", style="yellow")
    
    for match in matches:
        table.add_row(str(match[0]), match[1], f"{match[2]}/10", match[3])
    
    console.print(table)

@app.command()
def lead_close(lead_id: int = typer.Argument(..., help="Lead ID")):
    """Mark a lead as closed"""
    db.update_lead_status(lead_id, "closed")
    console.print(f"[green]✓[/green] Lead {lead_id} marked as closed")

@app.command()
def stats():
    """Show system statistics"""
    stats = db.get_stats()
    
    console.print("\n[bold cyan]System Statistics[/bold cyan]")
    console.print(f"Total Providers: {stats['providers']}")
    console.print(f"Total Leads: {stats['leads']}")
    console.print(f"Pending Leads: {stats['pending_leads']}")
    console.print(f"Average Provider Reliability: {stats['avg_reliability']:.1f}/10\n")

if __name__ == "__main__":
    app()
