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

export type NutrientProgressState = {
  consumed: number;
  target: number | null;
  remaining: number | null;
  exceeded: number;
  isExceeded: boolean;
  percent: number | null;
  fill: number;
  formattedPercent: string;
  isPartial: boolean;
  isTargetSet: boolean;
  statusText: string;
};

export function calculateNutrientProgress(
  consumed: number | null,
  target: number | null,
  partial = false,
  unit = 'kcal',
): NutrientProgressState {
  if (
    consumed === null ||
    partial ||
    !Number.isFinite(consumed) ||
    consumed < 0
  ) {
    return {
      consumed: consumed !== null && Number.isFinite(consumed) && consumed >= 0 ? consumed : 0,
      target: target !== null && Number.isFinite(target) ? target : null,
      remaining: null,
      exceeded: 0,
      isExceeded: false,
      percent: null,
      fill: 0,
      formattedPercent: '--',
      isPartial: true,
      isTargetSet: target !== null && Number.isFinite(target) && target > 0,
      statusText: 'Incomplete data',
    };
  }

  if (target === null || !Number.isFinite(target) || target <= 0) {
    return {
      consumed,
      target: target !== null && Number.isFinite(target) ? target : null,
      remaining: null,
      exceeded: 0,
      isExceeded: false,
      percent: null,
      fill: 0,
      formattedPercent: '--',
      isPartial: false,
      isTargetSet: false,
      statusText: target === 0 ? 'Tracking disabled' : 'Target not set',
    };
  }

  const percent = (consumed / target) * 100;
  const isExceeded = consumed > target;
  const rawRemaining = isExceeded ? 0 : target - consumed;
  const rawExceeded = isExceeded ? consumed - target : 0;
  const remaining = isExceeded ? 0 : Math.round(rawRemaining * 100) / 100;
  const exceeded = isExceeded ? Math.round(rawExceeded * 100) / 100 : 0;
  const fill = Math.min(100, Math.max(0, percent));
  const roundedPercent = Math.round(percent);

  const statusText = isExceeded
    ? `${unit === 'kcal' ? Math.round(exceeded) : exceeded.toFixed(1)} ${unit} exceeded`
    : `${unit === 'kcal' ? Math.round(remaining) : remaining.toFixed(1)} ${unit} remaining`;

  return {
    consumed,
    target,
    remaining,
    exceeded,
    isExceeded,
    percent,
    fill,
    formattedPercent: `${roundedPercent}%`,
    isPartial: false,
    isTargetSet: true,
    statusText,
  };
}

export type MacroDistribution = {
  proteinCalories: number;
  carbsCalories: number;
  fatCalories: number;
  proteinPct: number;
  carbsPct: number;
  fatPct: number;
};

export function calculateMacroDistribution(
  proteinGrams: number | null,
  carbsGrams: number | null,
  fatGrams: number | null,
): MacroDistribution {
  const pCal =
    proteinGrams !== null && Number.isFinite(proteinGrams) && proteinGrams > 0
      ? proteinGrams * 4
      : 0;
  const cCal =
    carbsGrams !== null && Number.isFinite(carbsGrams) && carbsGrams > 0
      ? carbsGrams * 4
      : 0;
  const fCal =
    fatGrams !== null && Number.isFinite(fatGrams) && fatGrams > 0
      ? fatGrams * 9
      : 0;
  const totalCal = pCal + cCal + fCal;
  if (totalCal <= 0) {
    return {
      proteinCalories: 0,
      carbsCalories: 0,
      fatCalories: 0,
      proteinPct: 0,
      carbsPct: 0,
      fatPct: 0,
    };
  }
  return {
    proteinCalories: pCal,
    carbsCalories: cCal,
    fatCalories: fCal,
    proteinPct: Math.round((pCal / totalCal) * 100),
    carbsPct: Math.round((cCal / totalCal) * 100),
    fatPct: Math.round((fCal / totalCal) * 100),
  };
}
