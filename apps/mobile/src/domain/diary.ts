import { scaleNutrients, meals, sumNutrients } from './food.ts';
import type { Food, FoodNutrients, Meal } from './food.ts';
export const nutrientKeys = [
  'calories',
  'protein',
  'carbs',
  'fat',
  'fiber',
] as const;
export function localDateKey(now = new Date()): string {
  return `${now.getFullYear().toString().padStart(4, '0')}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}`;
}
export function validDateKey(value: unknown): value is string {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value))
    return false;
  const [y, m, d] = value.split('-').map(Number);
  const date = new Date(y, m - 1, d, 12);
  return y >= 1900 && y <= 9999 && localDateKey(date) === value;
}
export function shiftDay(key: string, days: number): string {
  if (!validDateKey(key) || !Number.isInteger(days))
    throw new Error('Invalid diary date.');
  const [y, m, d] = key.split('-').map(Number);
  const result = localDateKey(new Date(y, m - 1, d + days, 12));
  if (!validDateKey(result))
    throw new Error('Date is outside the supported range.');
  return result;
}
export type DiaryEntry = {
  id: string;
  foodId: string | null;
  foodName: string;
  meal: Meal;
  date: string;
  grams: number;
  unit: 'g';
  referenceGrams: 100;
  reference: FoodNutrients;
  nutrients: FoodNutrients;
  preparation: string;
  source: string;
  status: 'illustrative' | 'verified';
  createdAt: string;
  updatedAt: string;
};
export function createEntry(
  food: Food,
  meal: Meal,
  date: string,
  grams: number,
  id: string,
  now: string,
): DiaryEntry {
  const entry: DiaryEntry = {
    id,
    foodId: food.id,
    foodName: food.name,
    meal,
    date,
    grams,
    unit: 'g',
    referenceGrams: 100,
    reference: { ...food.nutrients },
    nutrients: scaleNutrients(food.nutrients, grams),
    preparation: food.preparation,
    source: food.source,
    status: food.status,
    createdAt: now,
    updatedAt: now,
  };
  assertEntry(entry);
  return entry;
}
export type AIDiaryEntryInput = {
  id: string;
  foodName: string;
  meal: Meal;
  date: string;
  grams: number;
  calories: number | null;
  protein: number | null;
  carbs: number | null;
  fat: number | null;
  fiber?: number | null;
  preparation?: string;
  source?: string;
  now?: string;
};
export function createAIDiaryEntry(input: AIDiaryEntryInput): DiaryEntry {
  const {
    id,
    foodName,
    meal,
    date,
    grams,
    calories,
    protein,
    carbs,
    fat,
    fiber = 0,
    preparation = 'Recognized by Gemini AI',
    source = 'Gemini AI',
    now = new Date().toISOString(),
  } = input;
  const trimmedName = foodName.trim();
  if (!trimmedName) {
    throw new Error('Food name cannot be empty.');
  }
  if (!Number.isFinite(grams) || grams <= 0) {
    throw new RangeError('Portion must be a positive number of grams.');
  }
  if (!meals.includes(meal)) {
    throw new Error('Invalid meal category.');
  }
  if (!validDateKey(date)) {
    throw new Error('Invalid diary date.');
  }
  const checkVal = (
    v: number | null | undefined,
    name: string,
  ): number | null => {
    if (v === null || v === undefined) return null;
    if (!Number.isFinite(v) || v < 0) {
      throw new RangeError(`${name} must be a non-negative finite number.`);
    }
    return v;
  };
  const portion: FoodNutrients = {
    calories: checkVal(calories, 'Calories'),
    protein: checkVal(protein, 'Protein'),
    carbs: checkVal(carbs, 'Carbohydrates'),
    fat: checkVal(fat, 'Fat'),
    fiber: checkVal(fiber, 'Fiber'),
  };
  const reference = scaleNutrients(portion, 10000 / grams);
  const nutrients: FoodNutrients = { ...portion };
  const entry: DiaryEntry = {
    id,
    foodId: null,
    foodName: trimmedName,
    meal,
    date,
    grams,
    unit: 'g',
    referenceGrams: 100,
    reference,
    nutrients,
    preparation: preparation.trim() || 'Recognized by Gemini AI',
    source: source.trim() || 'Gemini AI',
    status: 'illustrative',
    createdAt: now,
    updatedAt: now,
  };
  assertEntry(entry);
  return entry;
}
export function editPortion(
  entry: DiaryEntry,
  grams: number,
  now: string,
): DiaryEntry {
  const edited = {
    ...entry,
    grams,
    nutrients: scaleNutrients(entry.reference, grams),
    updatedAt: now,
  };
  assertEntry(edited);
  return edited;
}
function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
function nutrientRecord(value: unknown): value is FoodNutrients {
  return (
    record(value) &&
    nutrientKeys.every(
      (key) =>
        value[key] === null ||
        (typeof value[key] === 'number' &&
          Number.isFinite(value[key]) &&
          value[key] >= 0),
    )
  );
}
export function assertEntry(value: unknown): asserts value is DiaryEntry {
  if (
    !record(value) ||
    !['id', 'foodName', 'preparation', 'source'].every(
      (key) => typeof value[key] === 'string' && value[key].trim().length > 0,
    ) ||
    !(value.foodId === null || typeof value.foodId === 'string') ||
    !meals.includes(value.meal as Meal) ||
    !validDateKey(value.date) ||
    typeof value.grams !== 'number' ||
    value.unit !== 'g' ||
    value.referenceGrams !== 100 ||
    !nutrientRecord(value.reference) ||
    !nutrientRecord(value.nutrients) ||
    !['illustrative', 'verified'].includes(value.status as string) ||
    !['createdAt', 'updatedAt'].every(
      (key) =>
        typeof value[key] === 'string' &&
        /^\d{4}-\d{2}-\d{2}T.*Z$/.test(value[key]) &&
        Number.isFinite(Date.parse(value[key])),
    )
  )
    throw new Error('Invalid diary record.');
  const expected = scaleNutrients(value.reference, value.grams);
  for (const key of nutrientKeys) {
    const a = expected[key],
      b = value.nutrients[key];
    if (
      a === null
        ? b !== null
        : b === null || Math.abs(a - b) > Math.max(1, Math.abs(a)) * 1e-10
    )
      throw new Error('Invalid nutrition snapshot.');
  }
}
export function decodeDiary(raw: string | null): DiaryEntry[] {
  if (raw === null) return [];
  const value: unknown = JSON.parse(raw);
  if (!record(value) || value.version !== 1 || !Array.isArray(value.entries))
    throw new Error('Unsupported or invalid diary document.');
  const ids = new Set<string>();
  const byDate = new Map<string, DiaryEntry[]>();
  for (const entry of value.entries) {
    assertEntry(entry);
    if (ids.has(entry.id)) throw new Error('Duplicate diary identity.');
    ids.add(entry.id);
    const day = byDate.get(entry.date);
    if (day) day.push(entry);
    else byDate.set(entry.date, [entry]);
  }
  for (const day of byDate.values()) diaryTotals(day);
  return value.entries;
}
export function diaryTotals(entries: readonly DiaryEntry[]) {
  return sumNutrients(entries.map((entry) => entry.nutrients));
}
