"""Constants for the myDinnerPlan Home Assistant integration."""

from datetime import timedelta
from typing import Any

DOMAIN = "mydinnerplan"
PLATFORMS = ["sensor", "calendar", "image", "todo"]
VERSION = "1.2.0"

DEFAULT_HOST = "https://mydinnerplan.com"
UPDATE_INTERVAL = timedelta(minutes=5)

CONF_HOST = "host"
CONF_TOKEN = "token"

FRONTEND_URL = "/mydinnerplan"
CARD_FILENAME = "mydinnerplan-cards.js"


def device_info(entry_id: str, host: str | None = None) -> dict[str, Any]:
    """Device registry payload shared by every entity."""
    info: dict[str, Any] = {
        "identifiers": {(DOMAIN, entry_id)},
        "name": "myDinnerPlan",
        "manufacturer": "myDinnerPlan",
        "model": "Household dinner plan",
        "sw_version": VERSION,
    }
    if host:
        info["configuration_url"] = f"{host.rstrip('/')}/home-assistant"
    return info
