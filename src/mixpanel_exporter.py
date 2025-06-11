import base64
import json
from datetime import datetime
from typing import List, Dict, Any
import requests
from rich.logging import RichHandler
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("rich")

class MixpanelExporter:
    def __init__(
        self,
        version: str,
        api_url: str,
        username: str,
        password: str,
        project_id: str,
        from_date: datetime,
        to_date: datetime
    ):
        self.version = version
        self.api_url = api_url
        self.token = self._basic_auth(username, password)
        self.from_date = from_date
        self.to_date = to_date
        self.project_id = project_id
        self.client = requests.Session()

    @staticmethod
    def _basic_auth(username: str, password: str) -> str:
        """Create basic auth token."""
        auth = f"{username}:{password}"
        return base64.b64encode(auth.encode()).decode()

    def export(self) -> List[Dict[str, Any]]:
        """Export data from Mixpanel."""
        # Format times to yyyy-mm-dd
        from_date = self.from_date.strftime("%Y-%m-%d")
        to_date = self.to_date.strftime("%Y-%m-%d")
        url = f"{self.api_url}/export?from_date={from_date}&to_date={to_date}&project_id={self.project_id}"

        try:
            response = self.client.get(
                url,
                headers={"Authorization": f"Basic {self.token}"}
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Export failed: {str(e)}")

        log.info("Successfully connected to Mixpanel API", extra={"status": response.status_code})
        log.info("Starting to read events...")

        # Process events
        events = []
        event_count = 0

        for line in response.iter_lines():
            if not line:
                continue

            try:
                raw_data = json.loads(line)
                formatted_data = self._format_data_line(raw_data)
                
                if formatted_data["distinct_id"] and formatted_data["time"]:
                    events.append(formatted_data)
                    event_count += 1
                    if event_count % 1000 == 0:
                        log.info(f"Processed {event_count} events")
                else:
                    log.info("Skipping event with no distinct_id or time", extra={"event": formatted_data["event"]})

            except json.JSONDecodeError as e:
                log.error(f"Error decoding JSON: {str(e)}")
                continue

        log.info(f"Finished reading {event_count} events", extra={"total_events": event_count})
        return events

    def _format_data_line(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """Format a raw data line from Mixpanel."""
        formatted_data = {
            "event": "$pageview" if line["event"] == "Pageview" else line["event"],
            "distinct_id": "",
            "time": None,
            "properties": {
                "$lib_version": f"leland/mp-to-ph@{self.version}"
            }
        }

        # Parse properties
        for k, v in line["properties"].items():
            if k == "distinct_id":
                formatted_data["distinct_id"] = v
            elif k == "time":
                # Convert seconds since epoch to datetime
                formatted_data["time"] = datetime.fromtimestamp(int(v))
            else:
                if k == "mp_lib":
                    formatted_data["properties"]["$lib"] = f"{v}-imported"
                elif k not in ["$mp_api_endpoint", "$mp_api_timestamp_ms", "mp_processing_time_ms"]:
                    formatted_data["properties"][k] = v

        return formatted_data
