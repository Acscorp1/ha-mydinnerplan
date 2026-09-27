"""Dinner and shopping sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MDPCoordinator


@dataclass(frozen=True, kw_only=True)
class MDPSensorDescription(SensorEntityDescription):
    """Sensor that reads from the snapshot dict."""

    value_fn: Callable[[dict[str, Any]], Any]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]]
    picture_fn: Callable[[dict[str, Any]], str | None] | None = None


def _week_day_attrs(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten week days for Markdown / custom cards."""
    attrs: dict[str, Any] = {"week": data.get("week") or []}
    for day in attrs["week"]:
        if not isinstance(day, dict):
            continue
        key = str(day.get("short_weekday") or day.get("weekday") or "").lower()[:3]
        if not key:
            continue
        attrs[f"{key}_state"] = day.get("state")
        attrs[f"{key}_image"] = day.get("recipe_image")
        attrs[f"{key}_url"] = day.get("meal_url") or day.get("recipe_url")
        attrs[f"{key}_servings"] = day.get("servings")
        attrs[f"{key}_attending"] = day.get("attending")
    return attrs


SENSORS: tuple[MDPSensorDescription, ...] = (
    MDPSensorDescription(
        key="tonight",
        translation_key="tonight",
        name="Dinner tonight",
        icon="mdi:food",
        value_fn=lambda data: data.get("state"),
        picture_fn=lambda data: data.get("recipe_image"),
        attrs_fn=lambda data: {
            "date": data.get("date"),
            "weekday": data.get("weekday"),
            "has_meal": data.get("has_meal"),
            "is_cooking": data.get("is_cooking"),
            "slot_label": data.get("slot_label"),
            "servings": data.get("servings"),
            "attending": data.get("attending"),
            "accompaniments": data.get("accompaniments"),
            "recipe_url": data.get("recipe_url"),
            "meal_url": data.get("meal_url"),
            "recipe_image": data.get("recipe_image"),
            "ingredients": data.get("ingredients") or [],
            "ingredient_count": data.get("ingredient_count"),
            "steps": data.get("steps") or [],
            "step_count": data.get("step_count"),
            "week_summary": data.get("week_summary"),
        },
    ),
    MDPSensorDescription(
        key="tomorrow",
        translation_key="tomorrow",
        name="Dinner tomorrow",
        icon="mdi:calendar-arrow-right",
        value_fn=lambda data: data.get("tomorrow_state"),
        picture_fn=lambda data: data.get("tomorrow_recipe_image"),
        attrs_fn=lambda data: {
            "date": data.get("tomorrow_date"),
            "weekday": data.get("tomorrow_weekday"),
            "has_meal": data.get("tomorrow_has_meal"),
            "is_cooking": data.get("tomorrow_is_cooking"),
            "slot_label": data.get("tomorrow_slot_label"),
            "recipe_name": data.get("tomorrow_recipe_name"),
            "recipe_image": data.get("tomorrow_recipe_image"),
            "recipe_url": data.get("tomorrow_recipe_url"),
            "meal_url": data.get("tomorrow_meal_url"),
            "servings": data.get("tomorrow_servings"),
            "attending": data.get("tomorrow_attending"),
        },
    ),
    MDPSensorDescription(
        key="week",
        translation_key="week",
        name="Dinner week",
        icon="mdi:calendar-week",
        value_fn=lambda data: data.get("week_summary"),
        picture_fn=lambda data: data.get("recipe_image"),
        attrs_fn=_week_day_attrs,
    ),
    MDPSensorDescription(
        key="shopping",
        translation_key="shopping",
        name="Dinner shopping needed",
        icon="mdi:cart-outline",
        native_unit_of_measurement="items",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("shopping_needed"),
        attrs_fn=lambda data: {
            "shopping_allowed": data.get("shopping_allowed"),
            "shopping_on_hand": data.get("shopping_on_hand"),
            "shopping_items": data.get("shopping_items"),
            "shopping_range": data.get("shopping_range"),
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add snapshot sensors."""
    coordinator: MDPCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MDPSensor(coordinator, entry, description) for description in SENSORS
    )


class MDPSensor(CoordinatorEntity[MDPCoordinator], SensorEntity):
    """A single myDinnerPlan sensor."""

    entity_description: MDPSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MDPCoordinator,
        entry: ConfigEntry,
        description: MDPSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "myDinnerPlan",
            "manufacturer": "myDinnerPlan",
            "model": "Household dinner plan",
            "configuration_url": f"{coordinator.host}/home-assistant",
            "sw_version": "1.1.0",
        }

    @property
    def native_value(self) -> Any:
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def entity_picture(self) -> str | None:
        if not self.coordinator.data or not self.entity_description.picture_fn:
            return None
        picture = self.entity_description.picture_fn(self.coordinator.data)
        return str(picture) if picture else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {}
        return self.entity_description.attrs_fn(self.coordinator.data)
