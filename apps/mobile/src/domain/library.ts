import {
  scaleNutrients,
  sumNutrients,
  foodNutrientKeys,
  searchFoods,
  parseGrams,
} from './food.ts';
import type { Food, FoodNutrients } from './food.ts';
import type { DiaryEntry } from './diary.ts';
export type CustomFood = {
  id: string;
  name: string;
  description: string;
  servingGrams: number;
  servingNutrients: FoodNutrients;
  createdAt: string;
  updatedAt: string;
};
export type Ingredient = {
  foodId: string;
  name: string;
  reference: FoodNutrients;
  grams: number;
};
export type Recipe = {
  id: string;
  name: string;
  description: string;
  ingredients: Ingredient[];
  yieldGrams: number;
  servings: number;
  createdAt: string;
  updatedAt: string;
};
export type Library = {
  version: 1;
  customFoods: CustomFood[];
  recipes: Recipe[];
  favourites: string[];
};
export const emptyLibrary = (): Library => ({
  version: 1,
  customFoods: [],
  recipes: [],
  favourites: [],
});
function bounded(value: unknown, min: number, max: number): value is number {
  return (
    typeof value === 'number' &&
    Number.isFinite(value) &&
    value >= min &&
    value <= max
  );
}
function name(value: unknown, max = 120, optional = false): value is string {
  return (
    typeof value === 'string' &&
    value.length <= max &&
    (optional || value.trim().length > 0)
  );
}
function id(value: unknown): value is string {
  return typeof value === 'string' && /^[a-zA-Z0-9:-]{1,120}$/.test(value);
}
function timestamp(value: unknown): value is string {
  return (
    typeof value === 'string' &&
    /^\d{4}-\d{2}-\d{2}T.*Z$/.test(value) &&
    Number.isFinite(Date.parse(value))
  );
}
function nutrients(value: FoodNutrients, max = 1000000) {
  if (
    !value ||
    foodNutrientKeys.some(
      (k) => value[k] !== null && !bounded(value[k], 0, max),
    )
  )
    throw Error(
      'Nutrients must be blank (unknown) or finite values from 0 to 1,000,000.',
    );
  return Object.fromEntries(
    foodNutrientKeys.map((k) => [k, value[k]]),
  ) as FoodNutrients;
}
export function customAsFood(item: CustomFood): Food {
  return {
    id: item.id,
    name: item.name,
    aliases: [item.description],
    category: 'Custom',
    preparation: 'User-created food',
    referenceGrams: 100,
    nutrients: scaleNutrients(item.servingNutrients, 10000 / item.servingGrams),
    status: 'illustrative',
    source: `User-entered estimates. ${item.description}`.trim(),
    servingGrams: item.servingGrams,
  };
}
export function recipeNutrition(recipe: Recipe) {
  if (
    !recipe.ingredients.length ||
    !bounded(recipe.yieldGrams, 0.1, 1000000) ||
    !bounded(recipe.servings, 0.1, 10000)
  )
    throw Error(
      'Add at least one ingredient, yield 0.1–1,000,000 g and 0.1–10,000 servings.',
    );
  const total = sumNutrients(
    recipe.ingredients.map((i) => scaleNutrients(i.reference, i.grams)),
  );
  const complete = Object.fromEntries(
    foodNutrientKeys.map((k) => [k, total.partial[k] ? null : total.values[k]]),
  ) as FoodNutrients;
  return {
    total,
    per100: scaleNutrients(complete, 10000 / recipe.yieldGrams),
    perServing: scaleNutrients(complete, 100 / recipe.servings),
    servingGrams: recipe.yieldGrams / recipe.servings,
  };
}
export function recipeAsFood(recipe: Recipe): Food {
  const calculated = recipeNutrition(recipe);
  return {
    id: recipe.id,
    name: recipe.name,
    aliases: [recipe.description],
    category: 'Recipes',
    preparation: 'Saved recipe',
    referenceGrams: 100,
    nutrients: calculated.per100,
    status: 'illustrative',
    source:
      `Recipe ingredient snapshots; estimates, not verified nutrition. ${recipe.description}`.trim(),
    servingGrams: calculated.servingGrams,
  };
}
export function validateLibrary(data: Library): Library {
  if (
    !data ||
    data.version !== 1 ||
    !Array.isArray(data.customFoods) ||
    !Array.isArray(data.recipes) ||
    !Array.isArray(data.favourites)
  )
    throw Error('Unsupported or invalid food library.');
  const seen = new Set<string>();
  const customFoods = data.customFoods.map((item) => {
    if (
      !item ||
      !id(item.id) ||
      !item.id.startsWith('custom:') ||
      seen.has(item.id) ||
      !name(item.name) ||
      !name(item.description, 500, true) ||
      !bounded(item.servingGrams, 0.1, 10000) ||
      !timestamp(item.createdAt) ||
      !timestamp(item.updatedAt)
    )
      throw Error(
        'Custom food needs a unique ID, name (1–120 characters), description up to 500 characters and serving 0.1–10,000 g.',
      );
    seen.add(item.id);
    const valid = {
      id: item.id,
      name: item.name.trim(),
      description: item.description.trim(),
      servingGrams: item.servingGrams,
      servingNutrients: nutrients(item.servingNutrients),
      createdAt: item.createdAt,
      updatedAt: item.updatedAt,
    };
    customAsFood(valid);
    return valid;
  });
  const recipes = data.recipes.map((item) => {
    if (
      !item ||
      !id(item.id) ||
      !item.id.startsWith('recipe:') ||
      seen.has(item.id) ||
      !name(item.name) ||
      !name(item.description, 500, true) ||
      !Array.isArray(item.ingredients) ||
      item.ingredients.length > 100 ||
      !timestamp(item.createdAt) ||
      !timestamp(item.updatedAt)
    )
      throw Error(
        'Recipe needs a unique ID, name (1–120 characters), description up to 500 characters and 1–100 ingredients.',
      );
    seen.add(item.id);
    const ingredientIds = new Set<string>();
    const ingredients = item.ingredients.map((i) => {
      if (
        !i ||
        !id(i.foodId) ||
        i.foodId.startsWith('recipe:') ||
        ingredientIds.has(i.foodId) ||
        !name(i.name) ||
        !bounded(i.grams, 0.1, 1000000)
      )
        throw Error(
          'Ingredients need distinct food IDs, names and quantities 0.1–1,000,000 g. Nested recipes are not supported.',
        );
      ingredientIds.add(i.foodId);
      return {
        foodId: i.foodId,
        name: i.name,
        reference: nutrients(i.reference, Number.MAX_VALUE),
        grams: i.grams,
      };
    });
    const valid = {
      id: item.id,
      name: item.name.trim(),
      description: item.description.trim(),
      ingredients,
      yieldGrams: item.yieldGrams,
      servings: item.servings,
      createdAt: item.createdAt,
      updatedAt: item.updatedAt,
    };
    recipeNutrition(valid);
    return valid;
  });
  if (
    data.favourites.some((f) => !id(f)) ||
    new Set(data.favourites).size !== data.favourites.length
  )
    throw Error('Invalid or duplicate favourites.');
  return { version: 1, customFoods, recipes, favourites: [...data.favourites] };
}
export function decodeLibrary(raw: string | null): Library {
  return raw === null ? emptyLibrary() : validateLibrary(JSON.parse(raw));
}
export function libraryFoods(
  library: Library,
  builtins: readonly Food[],
): Food[] {
  return [
    ...builtins,
    ...library.customFoods.map(customAsFood),
    ...library.recipes.map(recipeAsFood),
  ];
}
export function saveCustom(
  data: Library,
  item: CustomFood,
  editing = false,
): Library {
  const existing = data.customFoods.find((f) => f.id === item.id);
  if (editing && !existing)
    throw Error('Food no longer exists. Reload the library.');
  if (
    existing &&
    ((!editing && JSON.stringify(existing) !== JSON.stringify(item)) ||
      existing.createdAt !== item.createdAt)
  )
    throw Error('Food identity changed. Reload the library.');
  return validateLibrary({
    ...data,
    customFoods: existing
      ? data.customFoods.map((f) => (f.id === item.id ? item : f))
      : [...data.customFoods, item],
  });
}
export function saveRecipe(
  data: Library,
  item: Recipe,
  editing = false,
): Library {
  const existing = data.recipes.find((f) => f.id === item.id);
  if (editing && !existing)
    throw Error('Recipe no longer exists. Reload the library.');
  if (
    existing &&
    ((!editing && JSON.stringify(existing) !== JSON.stringify(item)) ||
      existing.createdAt !== item.createdAt)
  )
    throw Error('Recipe identity changed. Reload the library.');
  return validateLibrary({
    ...data,
    recipes: existing
      ? data.recipes.map((f) => (f.id === item.id ? item : f))
      : [...data.recipes, item],
  });
}
export function removeLibraryItem(data: Library, id: string): Library {
  return validateLibrary({
    ...data,
    customFoods: data.customFoods.filter((f) => f.id !== id),
    recipes: data.recipes.filter((f) => f.id !== id),
    favourites: data.favourites.filter((f) => f !== id),
  });
}
export function setFavourite(
  data: Library,
  id: string,
  value: boolean,
  builtins: readonly Food[],
): Library {
  if (value && !libraryFoods(data, builtins).some((f) => f.id === id))
    throw Error('This item is no longer available.');
  return validateLibrary({
    ...data,
    favourites: value
      ? [...new Set([...data.favourites, id])]
      : data.favourites.filter((f) => f !== id),
  });
}
export function ingredientFromFood(
  foodId: string,
  foods: readonly Food[],
  grams: number,
): Ingredient {
  const food = foods.find(
    (f) => f.id === foodId && !f.id.startsWith('recipe:'),
  );
  if (!food || !bounded(grams, 0.1, 1000000))
    throw Error(
      'Choose an available built-in/custom food and 0.1–1,000,000 grams.',
    );
  return {
    foodId: food.id,
    name: food.name,
    reference: { ...food.nutrients },
    grams,
  };
}
export function recentFoods(
  entries: readonly DiaryEntry[],
  available: readonly Food[],
  limit = 20,
): Food[] {
  const ids = [
    ...new Set(
      [...entries]
        .sort(
          (a, b) =>
            b.createdAt.localeCompare(a.createdAt) || b.id.localeCompare(a.id),
        )
        .map((e) => e.foodId),
    ),
  ];
  return ids
    .flatMap((id) => {
      const food = available.find((f) => f.id === id);
      return food ? [food] : [];
    })
    .slice(0, limit);
}
export type LibraryFilter =
  'All' | 'Favourites' | 'Recent' | 'Custom' | 'Recipes';
export function browseFoods(
  data: Library,
  builtins: readonly Food[],
  entries: readonly DiaryEntry[],
  filter: LibraryFilter,
  query: string,
): Food[] {
  const available = libraryFoods(data, builtins);
  const candidates =
    filter === 'Recent'
      ? recentFoods(entries, available)
      : available.filter((f) =>
          filter === 'Favourites'
            ? data.favourites.includes(f.id)
            : filter === 'Custom'
              ? f.id.startsWith('custom:')
              : filter === 'Recipes'
                ? f.id.startsWith('recipe:')
                : true,
        );
  return searchFoods(candidates, query);
}
export function portionGrams(
  input: string,
  mode: 'grams' | 'servings',
  food: Food | undefined,
): number | null {
  const quantity = parseGrams(input);
  if (quantity === null) return null;
  const grams =
    mode === 'grams'
      ? quantity
      : food?.servingGrams
        ? quantity * food.servingGrams
        : NaN;
  return Number.isFinite(grams) && grams > 0 ? grams : null;
}
export function foodOrigin(food: Food): string {
  return food.id.startsWith('custom:')
    ? 'User-created estimate'
    : food.id.startsWith('recipe:')
      ? 'Recipe / snapshot estimates'
      : 'Built-in illustrative food';
}
