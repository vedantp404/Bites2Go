import type { Food } from '../domain/food.ts';
import { foods } from './foods.ts';
import { kaggleFoods } from './kaggleFoods.ts';

// Unified food catalogue combining dataset-first imported Kaggle foods
// and the existing built-in Bites2Go catalogue (894 items).
// Order: Kaggle foods (tier 1), Built-in foods (tier 2).
export const unifiedFoods: readonly Food[] = [...kaggleFoods, ...foods];
