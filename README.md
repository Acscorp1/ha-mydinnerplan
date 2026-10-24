# myDinnerPlan for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/Acscorp1/ha-mydinnerplan.svg)](https://github.com/Acscorp1/ha-mydinnerplan/releases)

Custom Home Assistant integration for [myDinnerPlan](https://mydinnerplan.com). After you paste a read-only token, dashboard cards show tonight’s ingredients and steps and the shopping list. Tomorrow, recipe photos, a week overview, and a calendar are entities too.

Setup guide and token creation: [mydinnerplan.com/home-assistant](https://mydinnerplan.com/home-assistant)

## Install with HACS (recommended)

> **Not** Settings → Apps / Add-ons → Repositories. That store only accepts add-on repos.
> myDinnerPlan is a **custom integration** — install it through **HACS** (or the zip below).

1. Install [HACS](https://hacs.xyz/) if you do not have it yet.
2. Open **HACS** (sidebar), then **⋮ → Custom repositories**.
3. Add this repository:
   - **Repository:** `https://github.com/Acscorp1/ha-mydinnerplan`
   - **Category:** Integration
4. Search for **myDinnerPlan**, download/install it, then **restart Home Assistant**.
5. Go to **Settings → Devices & services → Add integration → myDinnerPlan**.
6. Paste a token from **myDinnerPlan → Account → Settings → Home Assistant**.

### Alternate path (same custom repository)

In Home Assistant with HACS installed:

1. **HACS → ⋮ (top right) → Custom repositories**
2. Paste `https://github.com/Acscorp1/ha-mydinnerplan`
3. Category: **Integration** → Add
4. Find **myDinnerPlan** under Integrations and download it

## Manual install

1. Download the latest release zip from [Releases](https://github.com/Acscorp1/ha-mydinnerplan/releases), or clone this repo.
2. Copy `custom_components/mydinnerplan` into your Home Assistant `config/custom_components/` folder.
3. Restart Home Assistant, then add the **myDinnerPlan** integration.

You can also download a ready-made zip from [mydinnerplan.com/home-assistant](https://mydinnerplan.com/home-assistant).

## Configuration

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| Access token | Yes | — | Create/revoke in Account Settings |
| Host URL | No | `https://mydinnerplan.com` | Use your self-hosted or staging URL if needed |

The integration only polls myDinnerPlan over HTTPS with the token you provide. Nothing is pushed into your home network.

## Entities

- `sensor.*_dinner_tonight` — recipe name, photo, ingredients, steps, and a `recipes` attribute for the recipe card
- `sensor.*_dinner_tomorrow` — same cook-card fields for tomorrow
- `sensor.*_dinner_week` — one-line week plus per-day image/url attributes
- `sensor.*_dinner_shopping_needed` — count, plus a `shopping_list` of quantities grouped by aisle (Household and Pro)
- `todo.*_shopping_list` — read-only to-do list of those grocery rows
- `todo.*_tonight_ingredients` / `todo.*_tonight_steps` — read-only lists for the built-in to-do card
- `calendar.*_dinner_plan` — all-day events with meal link and photo URL
- `image.*_tonight_recipe_photo` / `image.*_tomorrow_recipe_photo` — for Picture entity cards

Checking items off stays in myDinnerPlan. The to-do lists refresh on the next poll (about every 5 minutes).

Entity IDs can vary by Home Assistant version — pick them from the **myDinnerPlan** device page.

## Dashboard cards

The integration registers two Lovelace cards. Add them from the card picker, or paste:

```yaml
type: custom:mydinnerplan-recipe-card
entity: sensor.mydinnerplan_dinner_tonight

type: custom:mydinnerplan-shopping-card
entity: sensor.mydinnerplan_dinner_shopping_needed
```

Use the tomorrow sensor on a second recipe card. A built-in to-do card also works:

```yaml
type: todo-list
entity: todo.mydinnerplan_shopping_list
```

If your dashboard is in YAML mode, add this resource:

```yaml
resources:
  - url: /mydinnerplan/mydinnerplan-cards.js
    type: module
```

## Dashboard tips

```yaml
type: picture-entity
entity: image.mydinnerplan_tonight_recipe_photo
```

## Support

- Product docs: https://mydinnerplan.com/home-assistant
- Issues: https://github.com/Acscorp1/ha-mydinnerplan/issues
