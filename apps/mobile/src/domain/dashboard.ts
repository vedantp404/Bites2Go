export type Nutrients = {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
};
export type PreviewMeal = {
  name: string;
  entries: { name: string; nutrients: Nutrients }[];
};
export function totals(meals: PreviewMeal[]): Nutrients {
  const result = { calories: 0, protein: 0, carbs: 0, fat: 0 };
  for (const meal of meals)
    for (const entry of meal.entries) {
      for (const key of Object.keys(result) as (keyof Nutrients)[]) {
        const value = entry.nutrients[key];
        if (!Number.isFinite(value) || value < 0)
          throw new Error('Invalid preview nutrient');
        result[key] += value;
      }
    }
  return result;
}
export function progress(consumed: number, target: number) {
  if (!Number.isFinite(consumed) || consumed < 0)
    throw new Error('Invalid intake');
  if (!Number.isFinite(target) || target <= 0)
    return { percent: null, fill: 0, remaining: null };
  const percent = (consumed / target) * 100;
  return {
    percent,
    fill: Math.min(100, Math.max(0, percent)),
    remaining: target - consumed,
  };
}
