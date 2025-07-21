import os
import time
from typing import List, Dict, Any
from posthog import Posthog
from rich import print as rprint
from src.mapping import name_mapping

# Constants
DELAY_MS = 1  # Delay between posthog queue events to avoid overloading the API

def map_event_name(event: str, properties: Dict[str, Any]) -> str:
    """Map Mixpanel event names to PostHog event names."""
    # Handle special case for Leland+ Banner Click
    if event == 'Leland+ Banner Click':
        source = properties.get('source', '').lower()
        if source == 'srp':
            return 'srp--leland_plus_banner_click'
        elif source == 'article':
            return 'article_page--leland_plus_banner_click'
        elif source == 'post_checkout':
            return 'post_checkout--leland_plus_banner_click'
        else:
            return 'leland_plus_banner--click'
    
    # Handle regular mappings - if not found in mapping, return original event name
    return name_mapping.get(event, event)

def posthog_import(data: List[Dict[str, Any]]) -> None:
    """Import events from Mixpanel to Posthog."""
    client = get_posthog_client()
    
    for line in data:
        if line["event"] == "$mp_web_page_view":
            line["event"] = "$pageview"
        else:
            # Map the event name using our mapping function
            line["event"] = map_event_name(line["event"], line["properties"])
        
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
