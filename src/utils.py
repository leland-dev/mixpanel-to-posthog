import os
from datetime import datetime
from rich import print as rprint
from rich.prompt import Prompt

def validate_env():
    # Check if Mixpanel credentials are in env
    if not all([os.getenv("MIXPANEL_PROJECT_ID"), os.getenv("MIXPANEL_USERNAME"), os.getenv("MIXPANEL_PASSWORD")]):
        rprint("\n[cyan]Mixpanel Credentials[/cyan]")
        rprint("[cyan]See the README for reference on what these are and how to get them.\n[/cyan]")  
        exit(1)

    # Check if Posthog credentials are in env
    if not all([os.getenv("POSTHOG_ENDPOINT"), os.getenv("POSTHOG_PROJECT_KEY")]):
        rprint("\n[cyan]Posthog Credentials[/cyan]")
        rprint("[cyan]See the README for reference on what these are and how to get them.\n[/cyan]")
        exit(1)
    
    return True

def get_valid_date_range():
    while True:
        from_date = Prompt.ask("Enter from_date in the format YYYY-MM-DD")
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            break
        except ValueError:
            rprint("[red]Invalid date format. Please use YYYY-MM-DD[/red]")

    while True:
        to_date = Prompt.ask("Enter to_date in the format YYYY-MM-DD")
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            break
        except ValueError:
            rprint("[red]Invalid date format. Please use YYYY-MM-DD[/red]")
    
    return from_dt, to_dt