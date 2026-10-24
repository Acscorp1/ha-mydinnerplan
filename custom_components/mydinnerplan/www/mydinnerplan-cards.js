const CARD_VERSION = "1.2.0";

const STYLE = `
  :host { display: block; }
  ha-card { height: 100%; overflow: hidden; }
  .body { padding: 0 0 12px; }
  .hero { position: relative; min-height: 72px; background: var(--secondary-background-color, rgba(0,0,0,0.06)); }
  .hero img { display: block; width: 100%; height: 190px; object-fit: cover; }
  .hero-text { padding: 14px 16px 0; }
  .hero.has-photo .hero-text {
    position: absolute; left: 0; right: 0; bottom: 0;
    padding: 28px 16px 12px;
    background: linear-gradient(transparent, rgba(0,0,0,0.72));
    color: #fff;
  }
  h2 { margin: 0; font-size: 1.25rem; font-weight: 650; line-height: 1.25; }
  .meta { margin: 6px 0 0; color: var(--secondary-text-color); font-size: 0.9rem; }
  .hero.has-photo .meta { color: rgba(255,255,255,0.88); }
  .section { padding: 12px 16px 0; }
  .section h3 {
    margin: 0 0 8px; font-size: 0.75rem; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
    color: var(--secondary-text-color);
  }
  .recipe-name { margin: 14px 16px 0; font-size: 1rem; font-weight: 650; }
  ul, ol { list-style: none; margin: 0; padding: 0; }
  .ingredient, .shop-row, .step {
    display: grid; gap: 8px; align-items: start;
    padding: 7px 0; border-top: 1px solid var(--divider-color, rgba(127,127,127,0.25));
    line-height: 1.35;
  }
  .ingredient:first-child, .shop-row:first-child, .step:first-child { border-top: 0; }
  .step { grid-template-columns: 1.6rem 1fr; }
  .num {
    width: 1.6rem; height: 1.6rem; border-radius: 999px;
    display: grid; place-items: center;
    background: var(--primary-color); color: var(--text-primary-color, #fff);
    font-size: 0.75rem; font-weight: 700;
  }
  .group {
    margin: 12px 16px 0; font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.03em; text-transform: uppercase;
    color: var(--primary-text-color);
  }
  .shop-row { margin: 0 16px; }
  .sub { display: block; color: var(--secondary-text-color); font-size: 0.82rem; }
  .tag {
    display: inline-block; margin-left: 6px; font-size: 0.75rem;
    color: var(--secondary-text-color);
  }
  a.action {
    display: inline-block; margin: 12px 16px 0;
    color: var(--primary-color); font-weight: 650; text-decoration: none;
  }
  .empty, .note { margin: 0; padding: 14px 16px 4px; color: var(--secondary-text-color); }
  details { margin: 8px 16px 0; }
  summary { cursor: pointer; color: var(--secondary-text-color); font-size: 0.9rem; }
  .on-hand { opacity: 0.75; }
`;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null && text !== "") node.textContent = text;
  return node;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function styleNode() {
  const node = document.createElement("style");
  node.textContent = STYLE;
  return node;
}

function findEntity(hass, suffix) {
  if (!hass || !hass.states) return "";
  return Object.keys(hass.states).find((id) => id.endsWith(suffix)) || "";
}

function attr(state, key, fallbackKey) {
  const attributes = (state && state.attributes) || {};
  if (attributes[key] != null && attributes[key] !== "") return attributes[key];
  if (fallbackKey && attributes[fallbackKey] != null) return attributes[fallbackKey];
  return undefined;
}

class MyDinnerPlanRecipeCard extends HTMLElement {
  static getConfigForm() {
    return {
      schema: [
        {
          name: "entity",
          required: true,
          selector: { entity: { domain: "sensor" } },
        },
      ],
    };
  }

  static getStubConfig(hass) {
    return { entity: findEntity(hass, "_dinner_tonight") };
  }

  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error("Choose the dinner tonight or dinner tomorrow sensor.");
    }
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 6;
  }

  connectedCallback() {
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) return;
    const root = this.shadowRoot;
    root.replaceChildren(styleNode());
    const state = this._hass.states[this._config.entity];
    const card = document.createElement("ha-card");
    if (!state) {
      card.append(el("p", "empty", "That dinner sensor is not available yet."));
      root.append(card);
      return;
    }

    const title = attr(state, "recipe_name", "tomorrow_recipe_name") || state.state || "Dinner";
    const image = attr(state, "recipe_image", "tomorrow_recipe_image") || attr(state, "entity_picture");
    const recipes = this._recipes(state, title);
    const servings = attr(state, "servings", "tomorrow_servings");
    const attending = attr(state, "attending", "tomorrow_attending");
    const bits = [];
    if (servings) bits.push(`${servings} servings`);
    if (attending) bits.push(attending);
    const sides = attr(state, "accompaniments", "tomorrow_accompaniments");
    if (sides) bits.push(`With ${sides}`);

    const hero = el("div", image ? "hero has-photo" : "hero");
    if (image) {
      const img = document.createElement("img");
      img.src = image;
      img.alt = "";
      hero.append(img);
    }
    const heroText = el("div", "hero-text");
    heroText.append(el("h2", "", title));
    if (bits.length) heroText.append(el("p", "meta", bits.join(" · ")));
    hero.append(heroText);
    card.append(hero);

    const body = el("div", "body");
    if (!recipes.length) {
      body.append(el("p", "empty", state.state || "Nothing planned."));
    } else {
      recipes.forEach((recipe, index) => {
        if (index > 0 && recipe.name) {
          body.append(el("div", "recipe-name", recipe.name));
        }
        const ingredients = asArray(recipe.ingredients);
        if (ingredients.length) {
          const section = el("div", "section");
          section.append(el("h3", "", "Ingredients"));
          const list = document.createElement("ul");
          ingredients.forEach((item) => {
            const line = typeof item === "string" ? item : item.line || item.name || "";
            if (!line) return;
            const row = el("li", "ingredient");
            const text = el("span", "", line);
            if (item && item.optional) text.append(el("span", "tag", "optional"));
            row.append(text);
            list.append(row);
          });
          section.append(list);
          body.append(section);
        }
        const steps = asArray(recipe.steps).map((step) => (typeof step === "string" ? step : step.line || "")).filter(Boolean);
        if (steps.length) {
          const section = el("div", "section");
          section.append(el("h3", "", "Steps"));
          const list = document.createElement("ol");
          steps.forEach((step, stepIndex) => {
            const row = el("li", "step");
            row.append(el("span", "num", String(stepIndex + 1)));
            row.append(el("span", "", step));
            list.append(row);
          });
          section.append(list);
          body.append(section);
        }
      });
    }

    const mealUrl = attr(state, "meal_url", "tomorrow_meal_url");
    if (mealUrl) {
      const link = el("a", "action", "Open this dinner");
      link.href = mealUrl;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      body.append(link);
    }
    card.append(body);
    root.append(card);
  }

  _recipes(state, title) {
    const primary = asArray(attr(state, "recipes"));
    const fallback = asArray(state.attributes && state.attributes.tomorrow_recipes);
    const recipes = primary.length ? primary : fallback;
    if (recipes.length) return recipes;
    const ingredients = asArray(attr(state, "ingredients", "tomorrow_ingredients"));
    const steps = asArray(attr(state, "steps", "tomorrow_steps"));
    if (!ingredients.length && !steps.length) return [];
    return [{ name: title, role: "main", ingredients, steps }];
  }
}

class MyDinnerPlanShoppingCard extends HTMLElement {
  static getConfigForm() {
    return {
      schema: [
        {
          name: "entity",
          required: true,
          selector: { entity: { domain: "sensor" } },
        },
      ],
    };
  }

  static getStubConfig(hass) {
    return { entity: findEntity(hass, "_dinner_shopping_needed") };
  }

  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error("Choose the dinner shopping needed sensor.");
    }
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 5;
  }

  connectedCallback() {
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) return;
    const root = this.shadowRoot;
    root.replaceChildren(styleNode());
    const state = this._hass.states[this._config.entity];
    const card = document.createElement("ha-card");
    if (!state) {
      card.append(el("p", "empty", "That shopping sensor is not available yet."));
      root.append(card);
      return;
    }

    const attributes = state.attributes || {};
    const hero = el("div", "hero");
    const heroText = el("div", "hero-text");
    heroText.append(el("h2", "", "Shopping list"));
    const range = attributes.shopping_range;
    const count = state.state;
    const subtitle = [count != null && count !== "unknown" ? `${count} to buy` : "", range].filter(Boolean).join(" · ");
    if (subtitle) heroText.append(el("p", "meta", subtitle));
    hero.append(heroText);
    card.append(hero);

    const body = el("div", "body");
    if (attributes.shopping_allowed === false) {
      body.append(el("p", "note", "Shopping lists are included on Household and Pro."));
    } else {
      const items = this._items(attributes);
      const needed = items.filter((item) => !item.on_hand);
      const onHand = items.filter((item) => item.on_hand);
      if (!needed.length) {
        body.append(el("p", "note", "Nothing to buy for this plan."));
      } else {
        this._appendGroups(body, needed);
      }
      if (onHand.length) {
        const details = document.createElement("details");
        details.append(el("summary", "", `Already on hand (${onHand.length})`));
        const wrap = el("div", "on-hand");
        this._appendGroups(wrap, onHand, true);
        details.append(wrap);
        body.append(details);
      }
      if (attributes.shopping_url) {
        const link = el("a", "action", "Open in myDinnerPlan");
        link.href = attributes.shopping_url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        body.append(link);
      }
    }
    card.append(body);
    root.append(card);
  }

  _items(attributes) {
    const list = asArray(attributes.shopping_list);
    if (list.length) {
      return list.map((item) => (typeof item === "string" ? { line: item, name: item, on_hand: false } : item));
    }
    if (typeof attributes.shopping_items === "string" && attributes.shopping_items.trim()) {
      return attributes.shopping_items.split(",").map((name) => {
        const trimmed = name.trim();
        return { line: trimmed, name: trimmed, on_hand: false, group: "" };
      }).filter((item) => item.name);
    }
    return [];
  }

  _appendGroups(parent, items) {
    const groups = [];
    const index = new Map();
    items.forEach((item) => {
      const name = item.group || "Other";
      if (!index.has(name)) {
        index.set(name, groups.length);
        groups.push({ name, items: [] });
      }
      groups[index.get(name)].items.push(item);
    });
    const showGroup = groups.length > 1 || (groups[0] && groups[0].name && groups[0].name !== "Other");
    groups.forEach((group) => {
      if (showGroup) parent.append(el("div", "group", group.name));
      group.items.forEach((item) => {
        const row = el("div", "shop-row");
        row.append(el("span", "", item.line || item.name || ""));
        const extra = [item.used_on, item.note].filter(Boolean).join(" · ");
        if (extra) row.append(el("span", "sub", extra));
        parent.append(row);
      });
    });
  }
}

if (!customElements.get("mydinnerplan-recipe-card")) {
  customElements.define("mydinnerplan-recipe-card", MyDinnerPlanRecipeCard);
}
if (!customElements.get("mydinnerplan-shopping-card")) {
  customElements.define("mydinnerplan-shopping-card", MyDinnerPlanShoppingCard);
}

window.customCards = window.customCards || [];
[
  {
    type: "mydinnerplan-recipe-card",
    name: "myDinnerPlan recipe",
    description: "Tonight or tomorrow: photo, ingredients, and steps.",
    preview: true,
  },
  {
    type: "mydinnerplan-shopping-card",
    name: "myDinnerPlan shopping list",
    description: "Grocery list grouped by aisle, with quantities.",
    preview: true,
  },
].forEach((card) => {
  if (!window.customCards.some((existing) => existing.type === card.type)) {
    window.customCards.push(card);
  }
});

void CARD_VERSION;
