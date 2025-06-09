import os
import time
from typing import List, Dict, Any
from posthog import Posthog
from rich import print as rprint

# Constants
DELAY_MS = 1  # Delay between posthog queue events to avoid overloading the API

def posthog_import(data: List[Dict[str, Any]]) -> None:
    """Import events from Mixpanel to Posthog."""
    client = get_posthog_client()
    
    for line in data:
        if line["event"] == "$mp_web_page_view":
            line["event"] = "$pageview"
        
        # Construct properties
        properties = {}
        for k, v in line["properties"].items():
            properties[k] = v
        properties["$geoip_disable"] = True
        
        try:
            client.capture(
                distinct_id=line["distinct_id"],
                event=line["event"],
                properties=properties,
                timestamp=line["time"]
            )
        except Exception as e:
            rprint(f"\n[red]Error importing event: {line['event']}[/red]")
            raise e
        
        # Sleep in between to avoid overloading the API
        time.sleep(DELAY_MS / 1000)  # Convert to seconds

def get_posthog_client() -> Posthog:
    """Get Posthog client with credentials."""
    posthog_endpoint = os.getenv("POSTHOG_ENDPOINT")
    posthog_api_key = os.getenv("POSTHOG_PROJECT_KEY")
    posthog_personal_api_key = os.getenv("POSTHOG_API_KEY")
   
    # Create Posthog client
    try:
        client = Posthog(
            project_api_key=posthog_api_key,
            host=posthog_endpoint,
            personal_api_key=posthog_personal_api_key,
            historical_migration=True
        )
        return client
    except Exception as e:
        rprint(f"\n[red]Encountered an error while creating Posthog client: {str(e)}[/red]")
        exit(1)
