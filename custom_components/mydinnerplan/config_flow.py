"""UI setup for myDinnerPlan."""

from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol
from aiohttp import ClientError, ClientResponseError, ClientTimeout
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_HOST, CONF_TOKEN, DEFAULT_HOST, DOMAIN


class CannotConnect(Exception):
    """Host could not be reached."""


class InvalidAuth(Exception):
    """Token was rejected."""


async def validate_input(hass: HomeAssistant, host: str, token: str) -> str:
    """Return a title after a successful API check."""
    session = async_get_clientsession(hass)
    url = f"{host.rstrip('/')}/api/homeassistant"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    try:
        async with session.get(
            url, headers=headers, timeout=ClientTimeout(total=20)
        ) as response:
            if response.status == 401:
                raise InvalidAuth
            response.raise_for_status()
            data = await response.json(content_type=None)
    except InvalidAuth:
        raise
    except ClientResponseError as err:
        if err.status == 401:
            raise InvalidAuth from err
        raise CannotConnect from err
    except (ClientError, TimeoutError, OSError) as err:
        raise CannotConnect from err

    if not isinstance(data, dict) or "state" not in data:
        raise CannotConnect

    tonight = data.get("state") or "myDinnerPlan"
    return f"myDinnerPlan ({tonight})"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for myDinnerPlan."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Collect the token and optional host."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = str(user_input.get(CONF_HOST) or DEFAULT_HOST).strip()
            token = str(user_input.get(CONF_TOKEN) or "").strip()
            if not host.startswith("http"):
                host = f"https://{host}"
            try:
                title = await validate_input(self.hass, host, token)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                unique = hashlib.sha256(token.encode()).hexdigest()[:16]
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=title,
                    data={CONF_HOST: host, CONF_TOKEN: token},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TOKEN): str,
                    vol.Optional(CONF_HOST, default=DEFAULT_HOST): str,
                }
            ),
            errors=errors,
        )
