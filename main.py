import os
from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console

from src.utils import get_valid_date_range, validate_env
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

    # Export from Mixpanel and import to Posthog
    rprint("[blue]Exporting data from Mixpanel (This may take awhile)[/blue]")

    with console.status("[bold blue]Exporting data from Mixpanel (This may take a while)...", spinner="dots") as status:
        try:
            exporter = MixpanelExporter(
                version=VERSION,
                api_url=MIXPANEL_API_URL,
                username=os.getenv("MIXPANEL_USERNAME"),
                password=os.getenv("MIXPANEL_PASSWORD"),
                project_id=os.getenv("MIXPANEL_PROJECT_ID"),
                from_date=from_dt,
                to_date=to_dt
            )
            # You can update the status message dynamically inside the block
            status.update("[bold yellow]Exporting data from Mixpanel...", spinner="earth") # Example update
            data = exporter.export()

            # Change status message for the next phase
            status.update("[bold magenta]Importing data to Posthog...", spinner="line") # Example update
            posthog_import(data)

        except Exception as e:
            rprint(f"[red]Error during export/import: {str(e)}[/red]")
            exit(1)


    rprint("[green]Successfully imported data to Posthog[/green]")

if __name__ == "__main__":
    main() 