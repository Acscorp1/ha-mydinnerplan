"""Recipe photo entities for dashboard picture cards."""

from __future__ import annotations

from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import MDPCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add recipe image entities."""
    coordinator: MDPCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MDPRecipeImage(hass, coordinator, entry, "tonight", "Tonight recipe photo"),
            MDPRecipeImage(hass, coordinator, entry, "tomorrow", "Tomorrow recipe photo"),
        ]
    )


class MDPRecipeImage(CoordinatorEntity[MDPCoordinator], ImageEntity):
    """Remote recipe photo for picture-entity cards."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: MDPCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        ImageEntity.__init__(self, hass)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_image_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "myDinnerPlan",
            "manufacturer": "myDinnerPlan",
            "model": "Household dinner plan",
        }
        self._attr_image_url = self._url_from_data(coordinator.data)
        self._attr_image_last_updated = dt_util.utcnow()

    def _url_from_data(self, data: dict[str, Any] | None) -> str | None:
        if not data:
            return None
        if self._key == "tomorrow":
            url = data.get("tomorrow_recipe_image")
        else:
            url = data.get("recipe_image")
        return str(url) if url else None

    @callback
    def _handle_coordinator_update(self) -> None:
        new_url = self._url_from_data(self.coordinator.data)
        if new_url != self._attr_image_url:
            self._attr_image_url = new_url
            self._attr_image_last_updated = dt_util.utcnow()
            self._cached_image = None
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and bool(self._attr_image_url)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        if self._key == "tomorrow":
            return {
                "recipe_name": data.get("tomorrow_recipe_name"),
                "recipe_url": data.get("tomorrow_recipe_url"),
                "meal_url": data.get("tomorrow_meal_url"),
                "date": data.get("tomorrow_date"),
            }
        return {
            "recipe_name": data.get("recipe_name") or data.get("state"),
            "recipe_url": data.get("recipe_url"),
            "meal_url": data.get("meal_url"),
            "date": data.get("date"),
        }
