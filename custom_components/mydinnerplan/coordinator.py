"""Poll myDinnerPlan for dinner sensors."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL


class MDPCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the household snapshot once per interval."""

    def __init__(self, hass: HomeAssistant, host: str, token: str) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.host = host.rstrip("/")
        self._token = token

    async def _async_update_data(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        url = f"{self.host}/api/homeassistant"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        try:
            async with session.get(
                url, headers=headers, timeout=ClientTimeout(total=20)
            ) as response:
                if response.status == 401:
                    raise UpdateFailed("Invalid myDinnerPlan token")
                response.raise_for_status()
                data = await response.json(content_type=None)
        except ClientResponseError as err:
            raise UpdateFailed(f"myDinnerPlan HTTP {err.status}") from err
        except (ClientError, TimeoutError, OSError) as err:
            raise UpdateFailed(f"Could not reach myDinnerPlan: {err}") from err

        if not isinstance(data, dict):
            raise UpdateFailed("Unexpected myDinnerPlan response")
        return data
