export type FoodNutrients = {
  calories: number | null;
  protein: number | null;
  carbs: number | null;
  fat: number | null;
  fiber: number | null;
};
export type ExtendedNutrients = FoodNutrients & {
  sugar?: number | null;
  sodium?: number | null;
};
export type CommonServing = {
  description: string;
  grams: number;
};
export type Food = {
  id: string;
  name: string;
  aliases: readonly string[];
  category: string;
  subcategory?: string;
  preparation: string;
  referenceGrams: 100;
  nutrients: ExtendedNutrients;
  status: 'illustrative' | 'verified' | 'estimated';
  source: string;
  sourceId?: string;
  sourceNotes?: string;
  servingGrams?: number;
  servingUnit?: string;
  commonServings?: readonly CommonServing[];
  imageKey?: string;
};
export function searchFoods(foods: readonly Food[], query: string): Food[] {
  const term = query.trim().toLowerCase();
  const seen = new Set<string>();
  if (!term) {
    const list: Food[] = [];
    for (const food of foods) {
      if (!seen.has(food.id)) {
        seen.add(food.id);
        list.push(food);
      }
    }
    return list;
  }

  const tokens = term.split(/\s+/).filter(Boolean);
  const scored: { food: Food; score: number }[] = [];

  for (const food of foods) {
    if (seen.has(food.id)) continue;

    const name = food.name.toLowerCase();
    const aliases = food.aliases.map((a) => a.toLowerCase());
    const category = food.category.toLowerCase();
    const subcategory = (food.subcategory ?? '').toLowerCase();
    const searchable = [name, ...aliases, category, subcategory];

    let score = 0;

    // Exact matches (highest priority)
    if (name === term) {
      score = Math.max(score, 1000);
    } else if (aliases.includes(term)) {
      score = Math.max(score, 950);
    }

    // Prefix matches
    if (name.startsWith(term)) {
      score = Math.max(score, 800 + (term.length / name.length) * 50);
    } else if (aliases.some((a) => a.startsWith(term))) {
      const bestAlias = aliases.find((a) => a.startsWith(term))!;
      score = Math.max(score, 820 + (term.length / bestAlias.length) * 50);
    } else if (name.split(/\s+/).some((word) => word.startsWith(term))) {
      score = Math.max(score, 700);
    } else if (
      aliases.some((a) => a.split(/\s+/).some((w) => w.startsWith(term)))
    ) {
      score = Math.max(score, 650);
    }

    // Substring matches
    if (name.includes(term)) {
      score = Math.max(score, 600);
    } else if (aliases.some((a) => a.includes(term))) {
      score = Math.max(score, 500);
    } else if (category.includes(term) || subcategory.includes(term)) {
      score = Math.max(score, 400);
    }

    // Multi-token search
    if (tokens.length > 1) {
      const allTokensMatch = tokens.every((token) =>
        searchable.some((text) => text.includes(token)),
      );
      if (allTokensMatch) {
        const inNameTokens = tokens.every((token) => name.includes(token));
        score = Math.max(score, inNameTokens ? 550 : 450);
      }
    }

    if (score > 0) {
      // Dataset-first ranking:
      // Tier 1: Kaggle imported catalogue (+0.4)
      // Tier 2: Built-in catalogue (+0.2)
      // Tier 3: User-created custom foods and recipes (+0.0)
      const tierBonus =
        food.id.startsWith('kaggle:') || food.sourceId?.startsWith('kaggle:')
          ? 0.4
          : food.id.startsWith('custom:') || food.id.startsWith('recipe:')
            ? 0.0
            : 0.2;
      seen.add(food.id);
      scored.push({ food, score: score + tierBonus });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  return scored.map((item) => item.food);
}
export function parseGrams(input: string): number | null {
  const value = input.trim().replace(',', '.');
  if (!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(value)) return null;
  const grams = Number(value);
  return Number.isFinite(grams) && grams > 0 ? grams : null;
}
export function scaleNutrients(
  nutrients: FoodNutrients,
  grams: number,
): FoodNutrients {
  if (!Number.isFinite(grams) || grams <= 0)
    throw new RangeError('Enter a positive, finite portion in grams.');
  function scale(value: number | null): number | null {
    if (value === null) return null;
    if (!Number.isFinite(value) || value < 0)
      throw new RangeError('Invalid reference nutrition.');
    const result = value * (grams / 100);
    if (!Number.isFinite(result) || (value > 0 && result === 0))
      throw new RangeError('Portion is outside the supported numeric range.');
    return result;
  }
  return {
    calories: scale(nutrients.calories),
    protein: scale(nutrients.protein),
    carbs: scale(nutrients.carbs),
    fat: scale(nutrients.fat),
    fiber: scale(nutrients.fiber),
  };
}
export function formatNutrient(
  value: number | null,
  unit: 'kcal' | 'g',
): string {
  if (value === null) return 'Unknown';
  return `${value.toFixed(unit === 'kcal' ? 0 : 1)} ${unit}`;
}
export const meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner'] as const;
export type Meal = (typeof meals)[number];
export function mealContext(value: string | string[] | undefined): Meal | null {
  return meals.find((meal) => meal === value) ?? null;
}
export type FoodDraft = {
  meal: Meal | null;
  query: string;
  foodId: string | null;
  grams: string;
  detail: boolean;
  confirmed: boolean;
};
export function defaultFoodPortion(id: string | null | undefined): {
  mode: 'grams' | 'servings';
  quantity: string;
} {
  return id?.startsWith('recipe:')
    ? { mode: 'servings', quantity: '1' }
    : { mode: 'grams', quantity: '100' };
}
export function createDraft(value: string | string[] | undefined): FoodDraft {
  return {
    meal: mealContext(value),
    query: '',
    foodId: null,
    grams: '100',
    detail: false,
    confirmed: false,
  };
}
export type DraftAction =
  | { type: 'query'; value: string }
  | { type: 'meal'; value: Meal }
  | { type: 'select'; id: string }
  | { type: 'grams'; value: string }
  | { type: 'back' }
  | { type: 'confirm' };
export function foodDraftReducer(
  state: FoodDraft,
  action: DraftAction,
): FoodDraft {
  switch (action.type) {
    case 'meal':
      return { ...state, meal: action.value, confirmed: false };
    case 'query':
      return { ...state, query: action.value };
    case 'select':
      return {
        ...state,
        foodId: action.id,
        detail: true,
        grams:
          state.foodId === action.id
            ? state.grams
            : defaultFoodPortion(action.id).quantity,
        confirmed: state.foodId === action.id && state.confirmed,
      };
    case 'grams':
      return { ...state, grams: action.value, confirmed: false };
    case 'back':
      return { ...state, detail: false };
    case 'confirm':
      return state.foodId && parseGrams(state.grams) !== null
        ? { ...state, confirmed: true }
        : state;
  }
}

export const foodNutrientKeys = [
  'calories',
  'protein',
  'carbs',
  'fat',
  'fiber',
] as const;
export function sumNutrients(items: readonly FoodNutrients[]) {
  const values = {} as FoodNutrients;
  const partial = {} as Record<keyof FoodNutrients, boolean>;
  for (const key of foodNutrientKeys) {
    const known = items
      .map((item) => item[key])
      .filter((value) => value !== null);
    values[key] =
      items.length && !known.length ? null : known.reduce((a, b) => a + b, 0);
    partial[key] = known.length < items.length;
    if (values[key] !== null && !Number.isFinite(values[key]))
      throw Error('Nutrition total exceeds supported range.');
  }
  return { values, partial, count: items.length };
}
