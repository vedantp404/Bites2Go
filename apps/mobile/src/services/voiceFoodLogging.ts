/**
 * Voice food logging service: client API caller, natural language interpretation,
 * food catalogue matching, and diary persistence preparation.
 */

import {
  type Food,
  type FoodNutrients,
  type Meal,
  scaleNutrients,
  searchFoods,
} from '../domain/food.ts';
import {
  type DiaryEntry,
  createAIDiaryEntry,
  createEntry,
  assertEntry,
} from '../domain/diary.ts';
import { type Library, customAsFood, recipeAsFood } from '../domain/library.ts';
import { unifiedFoods } from '../data/unifiedFoods.ts';
import { getBackendBaseUrl } from './aiFoodRecognition.ts';

export type ParsedVoiceFoodItem = {
  food_description: string;
  quantity: number;
  unit: string;
  preparation?: string | null;
  state: 'raw' | 'cooked' | 'unspecified';
  estimated_grams: number;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low';
  alternatives: string[];
  notes?: string | null;
};

export type VoiceMealParseResponse = {
  success: boolean;
  transcript: string;
  summary: string;
  items: ParsedVoiceFoodItem[];
  warnings: string[];
  clarifying_questions: string[];
};

export type MatchedVoiceFoodCandidate = {
  id: string;
  stableEntryId: string;
  originalParsedItem: ParsedVoiceFoodItem;
  food_name: string;
  quantity: number;
  unit: string;
  estimated_grams: number;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  state: 'raw' | 'cooked' | 'unspecified';
  preparation: string;
  notes: string;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low';
  matchedCatalogueFood: Food | null;
  availableMatches: Food[];
  sourceMode: 'catalogue' | 'ai';
  reference: FoodNutrients;
};

/**
 * Send voice transcript to FastAPI backend for natural language food extraction.
 */
export async function parseVoiceMeal(
  transcript: string,
  mealContext?: string,
  loggedDate?: string,
): Promise<VoiceMealParseResponse> {
  const cleaned = transcript.trim();
  if (!cleaned) {
    throw new Error('Please speak or type a food description.');
  }

  const baseUrl = getBackendBaseUrl();
  const url = `${baseUrl}/api/v1/parse-voice-meal`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        transcript: cleaned,
        meal_context: mealContext,
        logged_date: loggedDate,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      let detail = `Error ${response.status}`;
      try {
        const errorJson = await response.json();
        detail = errorJson.detail || detail;
      } catch {
        // use default detail
      }
      throw new Error(detail);
    }

    return (await response.json()) as VoiceMealParseResponse;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error(
        'Voice interpretation request timed out. Please check your connection and try again.',
      );
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Build searchable pool of catalogue foods, including custom foods and recipes if available.
 */
export function buildAvailableFoodPool(
  library?: Library | null,
  baseFoods: readonly Food[] = unifiedFoods,
): Food[] {
  const custom = library?.customFoods?.map(customAsFood) ?? [];
  const recipes = library?.recipes?.map(recipeAsFood) ?? [];
  return [...baseFoods, ...custom, ...recipes];
}

/**
 * Match parsed voice food items to the existing 1,411-food unified catalogue,
 * preserving dataset-first priority and provenance.
 */
export function matchVoiceItemsToCatalogue(
  items: ParsedVoiceFoodItem[],
  availableFoods: readonly Food[],
): MatchedVoiceFoodCandidate[] {
  return items.map((item, index) => {
    const rawGrams = item.estimated_grams > 0 ? item.estimated_grams : 100;
    const query = item.food_description.trim();

    // Search existing catalogue using searchFoods (handles dataset-first ranking)
    const matches = searchFoods(availableFoods, query);

    // If query has 0 matches, also try searching the alternatives provided by Gemini
    const additionalMatches: Food[] = [];
    if (matches.length < 5 && item.alternatives?.length > 0) {
      for (const alt of item.alternatives) {
        if (!alt || !alt.trim()) continue;
        const altMatches = searchFoods(availableFoods, alt.trim());
        for (const m of altMatches) {
          if (
            !matches.some((existing) => existing.id === m.id) &&
            !additionalMatches.some((e) => e.id === m.id)
          ) {
            additionalMatches.push(m);
            if (matches.length + additionalMatches.length >= 8) break;
          }
        }
        if (matches.length + additionalMatches.length >= 8) break;
      }
    }

    const allMatches = [...matches, ...additionalMatches].slice(0, 8);
    const topMatch = allMatches.length > 0 ? allMatches[0] : null;

    // Determine initial sourceMode:
    // If we have a very close match in the catalogue, we can prefer catalogue data;
    // otherwise default to AI-estimated values.
    const isCloseMatch =
      topMatch !== null &&
      (topMatch.name.toLowerCase() === query.toLowerCase() ||
        topMatch.name.toLowerCase().includes(query.toLowerCase()) ||
        query.toLowerCase().includes(topMatch.name.toLowerCase()));

    const sourceMode: 'catalogue' | 'ai' = isCloseMatch ? 'catalogue' : 'ai';

    let calories = item.calories;
    let protein = item.protein;
    let carbohydrates = item.carbohydrates;
    let fat = item.fat;
    let reference: FoodNutrients;

    if (sourceMode === 'catalogue' && topMatch) {
      const scaled = scaleNutrients(topMatch.nutrients, rawGrams);
      calories = Math.round((scaled.calories ?? 0) * 10) / 10;
      protein = Math.round((scaled.protein ?? 0) * 10) / 10;
      carbohydrates = Math.round((scaled.carbs ?? 0) * 10) / 10;
      fat = Math.round((scaled.fat ?? 0) * 10) / 10;
      reference = { ...topMatch.nutrients };
    } else {
      // AI reference per 100g
      reference = scaleNutrients(
        {
          calories: item.calories,
          protein: item.protein,
          carbs: item.carbohydrates,
          fat: item.fat,
          fiber: 0,
        },
        10000 / rawGrams,
      );
    }

    const uniqueId = `voice-item-${Date.now()}-${index}`;
    const stableEntryId = `voice-entry-${Date.now()}-${index}-${Math.random().toString(36).substring(2, 8)}`;

    return {
      id: uniqueId,
      stableEntryId,
      originalParsedItem: item,
      food_name:
        topMatch && sourceMode === 'catalogue'
          ? topMatch.name
          : item.food_description,
      quantity: item.quantity,
      unit: item.unit,
      estimated_grams: rawGrams,
      calories,
      protein,
      carbohydrates,
      fat,
      state: item.state,
      preparation:
        item.preparation ||
        (item.state === 'raw' ? 'Raw / uncooked' : 'Cooked / prepared'),
      notes: item.notes || '',
      confidence: item.confidence,
      confidence_level: item.confidence_level,
      matchedCatalogueFood: topMatch,
      availableMatches: allMatches,
      sourceMode,
      reference,
    };
  });
}

/**
 * Validate and build diary entries from matched voice candidates for atomic persistence.
 */
export function buildDiaryEntriesFromVoiceCandidates(
  candidates: MatchedVoiceFoodCandidate[],
  meal: Meal,
  date: string,
  now: string = new Date().toISOString(),
): DiaryEntry[] {
  if (candidates.length === 0) {
    throw new Error('No food items to log.');
  }

  const entries: DiaryEntry[] = [];

  for (const item of candidates) {
    const trimmedName = item.food_name.trim();
    if (!trimmedName) {
      throw new Error('Food name cannot be empty.');
    }
    if (!Number.isFinite(item.estimated_grams) || item.estimated_grams <= 0) {
      throw new RangeError(
        `Portion for "${trimmedName}" must be a positive number of grams.`,
      );
    }
    if (
      !Number.isFinite(item.calories) ||
      item.calories < 0 ||
      !Number.isFinite(item.protein) ||
      item.protein < 0 ||
      !Number.isFinite(item.carbohydrates) ||
      item.carbohydrates < 0 ||
      !Number.isFinite(item.fat) ||
      item.fat < 0
    ) {
      throw new RangeError(
        `Nutritional values for "${trimmedName}" must be non-negative finite numbers.`,
      );
    }

    if (item.sourceMode === 'catalogue' && item.matchedCatalogueFood) {
      // Use verified or estimated catalogue entry
      const entry = createEntry(
        item.matchedCatalogueFood,
        meal,
        date,
        item.estimated_grams,
        item.stableEntryId,
        now,
      );
      assertEntry(entry);
      entries.push(entry);
    } else {
      // Use AI-estimated entry
      const entry = createAIDiaryEntry({
        id: item.stableEntryId,
        foodName: trimmedName,
        meal,
        date,
        grams: item.estimated_grams,
        calories: item.calories,
        protein: item.protein,
        carbs: item.carbohydrates,
        fat: item.fat,
        fiber: 0,
        preparation: item.preparation || 'Voice logged via Gemini AI',
        source: 'Gemini AI Voice Parser',
        now,
      });
      assertEntry(entry);
      entries.push(entry);
    }
  }

  return entries;
}
