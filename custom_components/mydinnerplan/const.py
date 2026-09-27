"""Constants for the myDinnerPlan Home Assistant integration."""

from datetime import timedelta

DOMAIN = "mydinnerplan"
PLATFORMS = ["sensor", "calendar", "image"]

DEFAULT_HOST = "https://mydinnerplan.com"
UPDATE_INTERVAL = timedelta(minutes=5)

CONF_HOST = "host"
CONF_TOKEN = "token"
