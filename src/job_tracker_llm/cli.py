"""
Main CLI application for the job tracker.
"""
import click
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text

from .models import JobOpportunity, Interaction, InteractionType, ContactMethod
from .storage import JobStorage
from .vector_store import JobVectorStore
from .utils import (
    prompt, prompt_choice, validate_email, validate_phone, validate_url,
    format_date, get_interest_level_description, get_status_color,
    truncate_text, get_interaction_type_display_name, get_contact_method_display_name
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for better output
console = Console()


@click.group()
@click.option('--data-dir', default='data/opportunities', help='Directory for opportunity data')
@click.option('--vector-dir', default='data/vector_index', help='Directory for vector index')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, data_dir: str, vector_dir: str, verbose: bool):
    """Job Tracker LLM - A comprehensive job search tracking tool."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize storage and vector store
    storage = JobStorage(data_dir)
    vector_store = JobVectorStore(storage, vector_dir)
    
    ctx.obj = {
        'storage': storage,
        'vector_store': vector_store
    }


@cli.command()
@click.pass_context
def add(ctx):
    """Add a new job opportunity."""
    storage = ctx.obj['storage']
    
    console.print(Panel.fit("Add New Job Opportunity", style="bold blue"))
    
    try:
        # Get basic information
        company = Prompt.ask("Company name")
        role = Prompt.ask("Role/title")
        
        # Get recruiter information
        recruiter_name = Prompt.ask("Recruiter name", default="")
        recruiter_contact = Prompt.ask("Recruiter email or phone", default="")
        
        # Validate contact information
        if recruiter_contact:
            if '@' in recruiter_contact and not validate_email(recruiter_contact):
                console.print("[yellow]Warning: Invalid email format[/yellow]")
            elif not validate_phone(recruiter_contact):
                console.print("[yellow]Warning: Invalid phone format[/yellow]")
        
        # Get additional details
        job_description = Prompt.ask("Job description (optional)", default="")
        resume_text = Prompt.ask("Resume used (optional)", default="")
        cover_letter_text = Prompt.ask("Cover letter used (optional)", default="")
        notes = Prompt.ask("General notes (optional)", default="")
        next_steps = Prompt.ask("Expected next steps (optional)", default="")
        company_link = Prompt.ask("Company/job posting URL (optional)", default="")
        source = Prompt.ask("Source (e.g., LinkedIn, referral) (optional)", default="")
        
        # Validate URL
        if company_link and not validate_url(company_link):
            console.print("[yellow]Warning: Invalid URL format[/yellow]")
        
        # Get interest level
        interest_choices = [f"{i} - {get_interest_level_description(i)}" for i in range(1, 6)]
        interest_choice = prompt_choice("Interest level", interest_choices, default_choice_index=2)
        interest_level = int(interest_choice.split(' - ')[0])
        
        # Get initial contact method
        contact_methods = [
            "recruiter_email",
            "recruiter_call", 
            "inbound_application",
            "linkedin_message",
            "referral"
        ]
        method_choice = prompt_choice(
            "How did the initial contact happen?",
            [get_contact_method_display_name(m) for m in contact_methods],
            default_choice_index=0
        )
        method = contact_methods[[get_contact_method_display_name(m) for m in contact_methods].index(method_choice)]
        
        initial_note = Prompt.ask("Notes about this first interaction (optional)", default="")
        
        # Create opportunity
        opportunity = JobOpportunity(
            company=company,
            role=role,
            recruiter_name=recruiter_name if recruiter_name else None,
            recruiter_contact=recruiter_contact if recruiter_contact else None,
            job_description=job_description if job_description else None,
            resume_text=resume_text if resume_text else None,
            cover_letter_text=cover_letter_text if cover_letter_text else None,
            notes=notes if notes else None,
            next_steps=next_steps if next_steps else None,
            company_link=company_link if company_link else None,
            source=source if source else None,
            interest_level=interest_level
        )
        
        # Add initial interaction
        initial_interaction = Interaction(
            type=InteractionType.INITIAL_CONTACT,
            method=ContactMethod(method),
            notes=initial_note if initial_note else None
        )
        opportunity.add_interaction(initial_interaction)
        
        # Save opportunity
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Saving opportunity...", total=None)
            filepath = storage.save_opportunity(opportunity)
            progress.update(task, completed=True)
        
        console.print(f"[green]✓ Opportunity saved to: {filepath}[/green]")
        
        # Update vector index
        if ctx.obj['vector_store'].vectorstore:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Updating search index...", total=None)
                ctx.obj['vector_store'].update_index()
                progress.update(task, completed=True)
            console.print("[green]✓ Search index updated[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Error adding opportunity: {e}")


@cli.command()
@click.pass_context
def list(ctx):
    """List all job opportunities."""
    storage = ctx.obj['storage']
    
    console.print(Panel.fit("Job Opportunities", style="bold blue"))
    
    try:
        opportunities = storage.list_opportunities()
        
        if not opportunities:
            console.print("[yellow]No opportunities found.[/yellow]")
            return
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Company", style="cyan")
        table.add_column("Role", style="cyan")
        table.add_column("Interest", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Last Contact", style="dim")
        table.add_column("File", style="dim")
        
        for opp in opportunities:
            status_color = get_status_color("active" if opp['active'] else opp.get('status', 'inactive'))
            status_text = "Active" if opp['active'] else opp.get('status', 'Inactive').title()
            
            last_contact = "None"
            if opp['latest_interaction']:
                last_contact = format_date(opp['latest_interaction'].date)
            
            table.add_row(
                opp['company'],
                opp['role'],
                f"{opp['interest_level']}/5",
                f"[{status_color}]{status_text}[/{status_color}]",
                last_contact,
                opp['filename']
            )
        
        console.print(table)
        console.print(f"\nTotal opportunities: {len(opportunities)}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Error listing opportunities: {e}")


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Maximum number of results')
@click.pass_context
def search(ctx, query: str, limit: int):
    """Search opportunities using AI-powered semantic search."""
    vector_store = ctx.obj['vector_store']
    
    console.print(Panel.fit(f"Search Results for: '{query}'", style="bold blue"))
    
    try:
        if not vector_store.vectorstore:
            console.print("[yellow]Vector search not available. Building index...[/yellow]")
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Building search index...", total=None)
                success = vector_store.build_index()
                progress.update(task, completed=True)
            
            if not success:
                console.print("[red]Failed to build search index[/red]")
                return
        
        # Perform search
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Searching...", total=None)
            results = vector_store.semantic_search(query, k=limit)
            progress.update(task, completed=True)
        
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return
        
        # Display results
        for i, result in enumerate(results, 1):
            opp = result.opportunity
            score = result.relevance_score or 0
            
            console.print(f"\n[bold cyan]{i}. {opp.company} - {opp.role}[/bold cyan]")
            console.print(f"   Interest: {opp.interest_level}/5 | Status: {'Active' if opp.active else 'Inactive'}")
            console.print(f"   Relevance: {score:.2%}")
            
            if opp.notes:
                console.print(f"   Notes: {truncate_text(opp.notes, 150)}")
            
            if opp.next_steps:
                console.print(f"   Next Steps: {truncate_text(opp.next_steps, 150)}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Error searching opportunities: {e}")


@cli.command()
@click.pass_context
def update(ctx):
    """Update an existing job opportunity."""
    storage = ctx.obj['storage']
    
    console.print(Panel.fit("Update Job Opportunity", style="bold blue"))
    
    try:
        opportunities = storage.list_opportunities()
        
        if not opportunities:
            console.print("[yellow]No opportunities found to update.[/yellow]")
            return
        
        # Show opportunities for selection
        console.print("Select an opportunity to update:")
        for i, opp in enumerate(opportunities, 1):
            status = "Active" if opp['active'] else "Inactive"
            console.print(f"  {i}. {opp['company']} - {opp['role']} ({status})")
        
        # Get selection
        choice = Prompt.ask("Enter number", default="1")
        try:
            index = int(choice) - 1
            if 0 <= index < len(opportunities):
                selected_opp = opportunities[index]
            else:
                console.print("[red]Invalid selection.[/red]")
                return
        except ValueError:
            console.print("[red]Invalid number.[/red]")
            return
        
        # Load opportunity
        opportunity = storage.load_opportunity(selected_opp['filepath'])
        
        # Show current details
        console.print(f"\n[bold]Current Details:[/bold]")
        console.print(f"Company: {opportunity.company}")
        console.print(f"Role: {opportunity.role}")
        console.print(f"Interest Level: {opportunity.interest_level}/5")
        console.print(f"Status: {'Active' if opportunity.active else 'Inactive'}")
        console.print(f"Next Steps: {opportunity.next_steps or 'None'}")
        
        # Update options
        while True:
            action = prompt_choice("What would you like to do?", [
                "Add interaction",
                "Update interest level",
                "Change next steps",
                "Update recruiter info",
                "Mark as inactive/rejected",
                "View full details",
                "Exit"
            ])
            
            if action == "Add interaction":
                interaction_type = prompt_choice("Interaction type:", [
                    "follow_up",
                    "interview_screen",
                    "interview_technical", 
                    "interview_final",
                    "rejection",
                    "offer",
                    "other"
                ])
                
                notes = Prompt.ask("Notes about this interaction (optional)", default="")
                
                interaction = Interaction(
                    type=InteractionType(interaction_type),
                    notes=notes if notes else None
                )
                opportunity.add_interaction(interaction)
                
                console.print("[green]✓ Interaction added[/green]")
                
            elif action == "Update interest level":
                interest_choices = [f"{i} - {get_interest_level_description(i)}" for i in range(1, 6)]
                interest_choice = prompt_choice("New interest level", interest_choices, default_choice_index=opportunity.interest_level-1)
                opportunity.interest_level = int(interest_choice.split(' - ')[0])
                console.print("[green]✓ Interest level updated[/green]")
                
            elif action == "Change next steps":
                opportunity.next_steps = Prompt.ask("Updated next steps")
                console.print("[green]✓ Next steps updated[/green]")
                
            elif action == "Update recruiter info":
                opportunity.recruiter_name = Prompt.ask("Recruiter name", default=opportunity.recruiter_name or "")
                opportunity.recruiter_contact = Prompt.ask("Recruiter contact", default=opportunity.recruiter_contact or "")
                console.print("[green]✓ Recruiter info updated[/green]")
                
            elif action == "Mark as inactive/rejected":
                status = prompt_choice("New status:", ["inactive", "rejected"])
                opportunity.active = False
                opportunity.status = status
                console.print(f"[green]✓ Status set to {status}[/green]")
                
            elif action == "View full details":
                console.print("\n[bold]Full Details:[/bold]")
                console.print(f"Company: {opportunity.company}")
                console.print(f"Role: {opportunity.role}")
                console.print(f"Recruiter: {opportunity.recruiter_name or 'None'}")
                console.print(f"Contact: {opportunity.recruiter_contact or 'None'}")
                console.print(f"Interest Level: {opportunity.interest_level}/5")
                console.print(f"Status: {'Active' if opportunity.active else opportunity.status}")
                console.print(f"Source: {opportunity.source or 'None'}")
                console.print(f"Next Steps: {opportunity.next_steps or 'None'}")
                console.print(f"Notes: {opportunity.notes or 'None'}")
                
                if opportunity.interactions:
                    console.print("\n[bold]Interactions:[/bold]")
                    for interaction in opportunity.interactions:
                        console.print(f"  {format_date(interaction.date)} - {get_interaction_type_display_name(interaction.type)}")
                        if interaction.notes:
                            console.print(f"    Notes: {interaction.notes}")
                
            elif action == "Exit":
                break
        
        # Save changes
        storage.update_opportunity(selected_opp['filepath'], opportunity)
        console.print(f"[green]✓ Changes saved to: {selected_opp['filepath']}[/green]")
        
        # Update vector index
        if ctx.obj['vector_store'].vectorstore:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Updating search index...", total=None)
                ctx.obj['vector_store'].update_index()
                progress.update(task, completed=True)
            console.print("[green]✓ Search index updated[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Error updating opportunity: {e}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show statistics about job opportunities."""
    storage = ctx.obj['storage']
    
    console.print(Panel.fit("Job Search Statistics", style="bold blue"))
    
    try:
        stats = storage.get_statistics()
        
        if stats['total'] == 0:
            console.print("[yellow]No opportunities found.[/yellow]")
            return
        
        # Create statistics table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Total Opportunities", str(stats['total']))
        table.add_row("Active Opportunities", str(stats['active']))
        table.add_row("Inactive Opportunities", str(stats['inactive']))
        table.add_row("Average Interest Level", f"{stats['avg_interest']:.1f}/5")
        
        console.print(table)
        
        # Status breakdown
        if stats['by_status']:
            console.print("\n[bold]By Status:[/bold]")
            for status, count in stats['by_status'].items():
                console.print(f"  {status.title()}: {count}")
        
        # Source breakdown
        if stats['by_source']:
            console.print("\n[bold]By Source:[/bold]")
            for source, count in stats['by_source'].items():
                console.print(f"  {source.title()}: {count}")
        
        # Check for overdue follow-ups
        overdue = storage.get_overdue_followups()
        if overdue:
            console.print(f"\n[bold yellow]⚠ {len(overdue)} opportunities need follow-up[/bold yellow]")
            for opp in overdue[:3]:  # Show first 3
                console.print(f"  • {opp['company']} - {opp['role']}")
            if len(overdue) > 3:
                console.print(f"  ... and {len(overdue) - 3} more")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Error getting statistics: {e}")


@cli.command()
@click.option('--output', '-o', default='job_opportunities.csv', help='Output CSV file')
@click.pass_context
def export(ctx, output: str):
    """Export opportunities to CSV format."""
    storage = ctx.obj['storage']
    
    console.print(Panel.fit("Export Opportunities", style="bold blue"))
    
    try:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Exporting to CSV...", total=None)
            storage.export_to_csv(output)
            progress.update(task, completed=True)
        
        console.print(f"[green]✓ Exported to: {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Error exporting opportunities: {e}")


@cli.command()
@click.pass_context
def build_index(ctx):
    """Build or rebuild the vector search index."""
    vector_store = ctx.obj['vector_store']
    
    console.print(Panel.fit("Build Search Index", style="bold blue"))
    
    try:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Building vector index...", total=None)
            success = vector_store.build_index()
            progress.update(task, completed=True)
        
        if success:
            console.print("[green]✓ Vector index built successfully[/green]")
        else:
            console.print("[red]✗ Failed to build vector index[/red]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Error building index: {e}")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
