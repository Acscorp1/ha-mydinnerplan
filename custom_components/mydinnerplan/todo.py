"""Read-only to-do lists for the shopping list, ingredients, and steps."""

from __future__ import annotations

import hashlib
from typing import Any

from homeassistant.components.todo import TodoItem, TodoItemStatus, TodoListEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, device_info
from .coordinator import MDPCoordinator


def _uid(prefix: str, label: str) -> str:
    digest = hashlib.sha1(label.encode()).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _items_from_rows(rows: list[Any], prefix: str, completed: bool = False) -> list[TodoItem]:
    items: list[TodoItem] = []
    for index, row in enumerate(rows, start=1):
        if isinstance(row, str):
            summary = row.strip()
            description = None
            key = f"{index}:{summary}"
            row_done = completed
        elif isinstance(row, dict):
            summary = str(row.get("line") or row.get("name") or "").strip()
            if row.get("optional") and summary:
                summary = f"{summary} (optional)"
            bits = [str(row.get("group") or "").strip(), str(row.get("used_on") or "").strip()]
            description = " · ".join(bit for bit in bits if bit) or None
            if row.get("note"):
                note = str(row["note"]).strip()
                description = f"{description} · {note}" if description and note else (note or description)
            key = f"{row.get('group') or ''}:{summary}"
            row_done = bool(row.get("on_hand"))
        else:
            continue
        if not summary:
            continue
        if prefix == "step":
            summary = f"{index}. {summary}"
        if description:
            description = description[:255]
        items.append(
            TodoItem(
                summary=summary[:255],
                uid=_uid(prefix, key or summary),
                status=TodoItemStatus.COMPLETED if row_done else TodoItemStatus.NEEDS_ACTION,
                description=description,
            )
        )
    return items


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add shopping, ingredient, and step lists."""
    coordinator: MDPCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MDPTodoList(coordinator, entry, "shopping", "Shopping list"),
            MDPTodoList(coordinator, entry, "ingredients", "Tonight ingredients"),
            MDPTodoList(coordinator, entry, "steps", "Tonight steps"),
        ]
    )


class MDPTodoList(CoordinatorEntity[MDPCoordinator], TodoListEntity):
    """A read-only list. Checking items stays in myDinnerPlan."""

    _attr_has_entity_name = True
    _attr_supported_features = 0

    def __init__(
        self,
        coordinator: MDPCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_todo_{key}"
        self._attr_device_info = device_info(entry.entry_id, coordinator.host)
        if key == "shopping":
            self._attr_icon = "mdi:cart-outline"
        elif key == "steps":
            self._attr_icon = "mdi:format-list-numbered"
        else:
            self._attr_icon = "mdi:food-variant"

    @property
    def todo_items(self) -> list[TodoItem] | None:
        data = self.coordinator.data
        if not data:
            return None
        if self._key == "shopping":
            if not data.get("shopping_allowed"):
                return []
            return _items_from_rows(list(data.get("shopping_list") or []), "shop")
        if self._key == "ingredients":
            recipes = data.get("recipes") or []
            if recipes:
                rows: list[Any] = []
                for recipe in recipes:
                    if not isinstance(recipe, dict):
                        continue
                    for item in recipe.get("ingredients") or []:
                        if isinstance(item, dict):
                            row = dict(item)
                            if len(recipes) > 1 and recipe.get("name"):
                                row["group"] = str(recipe.get("name"))
                            rows.append(row)
                return _items_from_rows(rows, "ing")
            return _items_from_rows(list(data.get("ingredients") or []), "ing")
        steps: list[Any] = []
        for recipe in data.get("recipes") or []:
            if not isinstance(recipe, dict):
                continue
            for step in recipe.get("steps") or []:
                text = str(step).strip()
                if not text:
                    continue
                if len(data.get("recipes") or []) > 1 and recipe.get("name"):
                    text = f"{recipe.get('name')}: {text}"
                steps.append(text)
        if not steps:
            steps = list(data.get("steps") or [])
        return _items_from_rows(steps, "step")
