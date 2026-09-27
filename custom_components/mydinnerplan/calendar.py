"""Week calendar from the dinner snapshot."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MDPCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add the week calendar."""
    coordinator: MDPCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MDPCalendar(coordinator, entry)])


def _event_from_day(day: dict[str, Any]) -> CalendarEvent | None:
    if not day.get("has_meal"):
        return None
    raw_date = day.get("date")
    if not raw_date:
        return None
    start = date.fromisoformat(str(raw_date))
    summary = str(day.get("state") or day.get("recipe_name") or day.get("slot_label") or "Dinner")

    parts: list[str] = []
    if day.get("slot_label"):
        parts.append(str(day["slot_label"]))
    if day.get("servings"):
        parts.append(f"{day['servings']} servings")
    if day.get("attending"):
        parts.append(f"Eating: {day['attending']}")
    if day.get("accompaniments"):
        parts.append(f"With: {day['accompaniments']}")
    if day.get("recipe_image"):
        parts.append(f"Photo: {day['recipe_image']}")
    if day.get("meal_url"):
        parts.append(f"Open: {day['meal_url']}")

    return CalendarEvent(
        start=start,
        end=start + timedelta(days=1),
        summary=summary,
        description="\n".join(parts) if parts else None,
        location=str(day.get("meal_url") or day.get("recipe_url") or "") or None,
        uid=f"mydinnerplan-{raw_date}",
    )


class MDPCalendar(CoordinatorEntity[MDPCoordinator], CalendarEntity):
    """All-day events for planned dinners this week."""

    _attr_has_entity_name = True
    _attr_name = "Dinner plan"
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator: MDPCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "myDinnerPlan",
            "manufacturer": "myDinnerPlan",
            "model": "Household dinner plan",
        }

    @property
    def entity_picture(self) -> str | None:
        data = self.coordinator.data or {}
        picture = data.get("recipe_image")
        return str(picture) if picture else None

    def _events(self) -> list[CalendarEvent]:
        week = (self.coordinator.data or {}).get("week") or []
        events: list[CalendarEvent] = []
        for day in week:
            if isinstance(day, dict):
                event = _event_from_day(day)
                if event:
                    events.append(event)
        return events

    @property
    def event(self) -> CalendarEvent | None:
        today = date.today()
        for event in self._events():
            if event.start <= today < event.end:
                return event
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        start = start_date.date()
        end = end_date.date()
        return [
            event
            for event in self._events()
            if event.start < end and event.end > start
        ]
