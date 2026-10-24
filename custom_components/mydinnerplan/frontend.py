"""Serve the recipe and shopping Lovelace cards with the integration."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from homeassistant.core import CoreState, Event, HomeAssistant
from homeassistant.helpers.event import async_call_later

from .const import CARD_FILENAME, DOMAIN, FRONTEND_URL, VERSION

_LOGGER = logging.getLogger(__name__)
_REGISTERED = f"{DOMAIN}_frontend_registered"
_ATTEMPTS = f"{DOMAIN}_frontend_attempts"
_MAX_ATTEMPTS = 12


def _card_url() -> str:
    return f"{FRONTEND_URL}/{CARD_FILENAME}?v={VERSION}"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register the card script once, after Lovelace is ready."""
    if hass.data.get(_REGISTERED):
        return
    hass.data[_REGISTERED] = True
    await _async_register_path(hass)

    async def _when_started(_event: Event | None = None) -> None:
        await _async_register_resource(hass)

    if hass.state == CoreState.running:
        await _when_started()
    else:
        hass.bus.async_listen_once("homeassistant_started", _when_started)


async def _async_register_path(hass: HomeAssistant) -> None:
    www = Path(__file__).parent / "www"
    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(FRONTEND_URL, str(www), False)]
        )
    except RuntimeError:
        _LOGGER.debug("myDinnerPlan card path already registered")
    except (AttributeError, ImportError):
        hass.http.register_static_path(FRONTEND_URL, str(www), False)


async def _async_register_resource(hass: HomeAssistant) -> None:
    attempts = int(hass.data.get(_ATTEMPTS, 0)) + 1
    hass.data[_ATTEMPTS] = attempts

    lovelace = hass.data.get("lovelace")
    mode = None
    resources = None
    if lovelace is not None:
        mode = getattr(lovelace, "mode", None)
        if mode is None and isinstance(lovelace, dict):
            mode = lovelace.get("mode")
        resources = getattr(lovelace, "resources", None)
        if resources is None and isinstance(lovelace, dict):
            resources = lovelace.get("resources")

    if mode == "yaml":
        _register_yaml_module(hass)
        return

    loaded = getattr(resources, "loaded", None) if resources is not None else None
    if resources is None or loaded is False:
        if attempts < _MAX_ATTEMPTS:

            async def _later(_now: datetime) -> None:
                await _async_register_resource(hass)

            async_call_later(hass, 5, _later)
            return
        _LOGGER.warning(
            "Lovelace resources were not ready. Add %s as a dashboard module resource",
            _card_url(),
        )
        _register_yaml_module(hass)
        return

    try:
        await _async_upsert_module(resources)
    except Exception:
        _LOGGER.exception("Could not add the myDinnerPlan dashboard card resource")
        _register_yaml_module(hass)


def _register_yaml_module(hass: HomeAssistant) -> None:
    try:
        from homeassistant.components.frontend import add_extra_js_url
    except ImportError:
        _LOGGER.warning(
            "Add %s as a Lovelace module resource to use the myDinnerPlan cards",
            _card_url(),
        )
        return
    add_extra_js_url(hass, _card_url())


async def _async_upsert_module(resources: object) -> None:
    url = _card_url()
    path = url.split("?", 1)[0]
    items = resources.async_items()  # type: ignore[attr-defined]
    for resource in items:
        current = str(resource.get("url") or "")
        if current.split("?", 1)[0] != path:
            continue
        if current != url:
            await resources.async_update_item(  # type: ignore[attr-defined]
                resource["id"],
                {"res_type": "module", "url": url},
            )
        return
    await resources.async_create_item({"res_type": "module", "url": url})  # type: ignore[attr-defined]
