# myDinnerPlan for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/Acscorp1/ha-mydinnerplan.svg)](https://github.com/Acscorp1/ha-mydinnerplan/releases)

Custom Home Assistant integration for [myDinnerPlan](https://mydinnerplan.com). After you paste a read-only token, tonight’s dinner (with recipe photo), tomorrow, shopping counts, a week overview, and a calendar show up as entities.

Setup guide and token creation: [mydinnerplan.com/home-assistant](https://mydinnerplan.com/home-assistant)

## Install with HACS (recommended)

1. Install [HACS](https://hacs.xyz/) if you do not have it yet.
2. Open **HACS → Integrations** (or **HACS → ⋮ → Custom repositories**).
3. Add this repository as a custom repository:
   - **Repository:** `Acscorp1/ha-mydinnerplan`
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

- `sensor.*_dinner_tonight` — recipe name; picture, ingredients, and steps as attributes
- `sensor.*_dinner_tomorrow`
- `sensor.*_dinner_week` — one-line week plus per-day image/url attributes
- `sensor.*_dinner_shopping_needed` — Household and Pro plans
- `calendar.*_dinner_plan` — all-day events with meal link and photo URL
- `image.*_tonight_recipe_photo` / `image.*_tomorrow_recipe_photo` — for Picture entity cards

Entity IDs can vary by Home Assistant version — pick them from the **myDinnerPlan** device page.

## Dashboard tips

```yaml
type: picture-entity
entity: image.mydinnerplan_tonight_recipe_photo

type: entities
entities:
  - sensor.mydinnerplan_dinner_tonight
  - sensor.mydinnerplan_dinner_tomorrow
  - calendar.mydinnerplan_dinner_plan
```

## Support

- Product docs: https://mydinnerplan.com/home-assistant
- Issues: https://github.com/Acscorp1/ha-mydinnerplan/issues
