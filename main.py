import os
import time
from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress

from src.utils import get_valid_date_range, validate_env, chunk_date_range, get_chunk_size
from src.mixpanel_exporter import MixpanelExporter
from src.posthog_importer import posthog_import


# Constants
VERSION = "dev"
DELAY_MS = 1  # Delay between posthog queue events to avoid overloading the API
MIXPANEL_API_URL = "https://data.mixpanel.com/api/2.0"

console = Console()

def main():
    load_dotenv()

    rprint("------------------------------------")
    rprint("[green]SC Mixpanel to Posthog Data Migrator[/green]")
    rprint("------------------------------------")

    # Check for mixpanel and posthog credentials
    validate_env()

    # Get date range
    rprint("\n[yellow]WARNING: If you have a large dataset, consider entering smaller date ranges at a time.[/yellow]")
    rprint("[yellow]You may crash your machine if you try to export too much data at once.\n[/yellow]")
    
    from_dt, to_dt = get_valid_date_range()
    chunk_size = get_chunk_size()
    
    # Split date range into chunks
    date_chunks = chunk_date_range(from_dt, to_dt, chunk_size)
    total_chunks = len(date_chunks)
    
    rprint(f"\n[blue]Processing {total_chunks} chunks of {chunk_size} days each[/blue]")
    rprint(f"[blue]Total date range: {from_dt.strftime('%Y-%m-%d')} to {to_dt.strftime('%Y-%m-%d')}[/blue]")

    start_time = time.time()
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing chunks...", total=total_chunks)
        
        for chunk_start, chunk_end in date_chunks:
            progress.update(task, description=f"[cyan]Processing {chunk_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")
            
            try:
                chunk_exporter = MixpanelExporter(
                    version=VERSION,
                    api_url=MIXPANEL_API_URL,
                    username=os.getenv("MIXPANEL_USERNAME"),
                    password=os.getenv("MIXPANEL_PASSWORD"),
                    project_id=os.getenv("MIXPANEL_PROJECT_ID"),
                    from_date=chunk_start,
                    to_date=chunk_end
                )
                
                data = chunk_exporter.export()
                posthog_import(data)
                
            except Exception as e:
                rprint(f"\n[red]Error processing chunk {chunk_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}: {str(e)}[/red]")
                exit(1)
            
            progress.advance(task)
    total_time = time.time() - start_time
    rprint(f"[green]Successfully imported all data to Posthog[/green] in {total_time:.2f} seconds / {total_time/60:.2f} minutes")

if __name__ == "__main__":
    main() 