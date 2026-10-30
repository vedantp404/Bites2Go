export type FoodNutrients = {
  calories: number | null;
  protein: number | null;
  carbs: number | null;
  fat: number | null;
  fiber: number | null;
};
export type Food = {
  id: string;
  name: string;
  aliases: readonly string[];
  category: string;
  preparation: string;
  referenceGrams: 100;
  nutrients: FoodNutrients;
  status: 'illustrative';
  source: string;
};
export function searchFoods(foods: readonly Food[], query: string): Food[] {
  const term = query.trim().toLowerCase();
  const seen = new Set<string>();
  return foods.filter((food) => {
    if (seen.has(food.id)) return false;
    const match = [food.name, ...food.aliases].some((name) =>
      name.toLowerCase().includes(term),
    );
    if (match) seen.add(food.id);
    return match;
  });
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
        grams: state.foodId === action.id ? state.grams : '100',
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
