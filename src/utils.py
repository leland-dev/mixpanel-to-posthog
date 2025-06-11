import os
from datetime import datetime, timedelta
from rich import print as rprint
from rich.prompt import Prompt, IntPrompt

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

def get_chunk_size() -> int:
    """Get the chunk size in days from the user."""
    while True:
        chunk_size = IntPrompt.ask(
            "Enter chunk size in days",
            default=7,
            show_default=True
        )
        if chunk_size > 0:
            return chunk_size
        rprint("[red]Chunk size must be greater than 0[/red]")

def chunk_date_range(from_date: datetime, to_date: datetime, chunk_size_days: int = 7) -> list[tuple[datetime, datetime]]:
    """
    Split a date range into smaller chunks.
    
    Args:
        from_date: Start date
        to_date: End date
        chunk_size_days: Number of days in each chunk (default: 7)
    
    Returns:
        List of (chunk_start, chunk_end) datetime tuples
    """
    chunks = []
    current_date = from_date
    
    while current_date < to_date:
        chunk_end = min(current_date + timedelta(days=chunk_size_days), to_date)
        chunks.append((current_date, chunk_end))
        current_date = chunk_end + timedelta(days=1)
    
    return chunks