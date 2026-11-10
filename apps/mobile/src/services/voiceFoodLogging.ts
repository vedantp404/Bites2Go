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
  calories: number | null;
  protein: number | null;
  carbohydrates: number | null;
  fat: number | null;
  fiber?: number | null;
  state: 'raw' | 'cooked' | 'unspecified';
  preparation: string;
  notes: string;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low';
  matchedCatalogueFood: Food | null;
  availableMatches: Food[];
  sourceMode: 'catalogue' | 'ai';
  origin?: 'ai' | 'offline_catalogue';
  reference: FoodNutrients;
};

export type OfflineVoiceMatchResult = {
  transcript: string;
  summary: string;
  candidates: MatchedVoiceFoodCandidate[];
  unmatchedClauses: string[];
  warnings: string[];
};

export class VoiceCloudError extends Error {
  status?: number;
  retryAfterSeconds?: number;
  errorCategory?: string;

  constructor(
    message: string,
    opts?: {
      status?: number;
      retryAfterSeconds?: number;
      errorCategory?: string;
    },
  ) {
    super(message);
    this.name = 'VoiceCloudError';
    this.status = opts?.status;
    this.retryAfterSeconds = opts?.retryAfterSeconds;
    this.errorCategory = opts?.errorCategory;
  }
}

function roundNutrient1(value: number | null): number | null {
  if (value === null) return null;
  return Math.round(value * 10) / 10;
}

export function scaleFoodNutrientsNullable(
  nutrients: FoodNutrients,
  grams: number,
): {
  calories: number | null;
  protein: number | null;
  carbohydrates: number | null;
  fat: number | null;
  fiber: number | null;
} {
  const scaled = scaleNutrients(nutrients, grams);
  return {
    calories: roundNutrient1(scaled.calories),
    protein: roundNutrient1(scaled.protein),
    carbohydrates: roundNutrient1(scaled.carbs),
    fat: roundNutrient1(scaled.fat),
    fiber: roundNutrient1(scaled.fiber),
  };
}

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
  const timeoutId = setTimeout(() => controller.abort(), 40000);

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
        if (typeof errorJson?.detail === 'string') {
          detail = errorJson.detail;
        } else if (errorJson?.detail?.message) {
          detail = errorJson.detail.message;
        }
      } catch {
        // use default detail
      }
      const rawRetryAfter = response.headers?.get?.('Retry-After');
      const retryAfterNum = rawRetryAfter ? Number(rawRetryAfter) : NaN;
      const errorCategory = response.headers?.get?.('X-Error-Category') ?? undefined;
      throw new VoiceCloudError(detail, {
        status: response.status,
        retryAfterSeconds: Number.isFinite(retryAfterNum) ? retryAfterNum : undefined,
        errorCategory,
      });
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

    let calories: number | null = item.calories;
    let protein: number | null = item.protein;
    let carbohydrates: number | null = item.carbohydrates;
    let fat: number | null = item.fat;
    let fiber: number | null = 0;
    let reference: FoodNutrients;

    if (sourceMode === 'catalogue' && topMatch) {
      const scaled = scaleFoodNutrientsNullable(topMatch.nutrients, rawGrams);
      calories = scaled.calories;
      protein = scaled.protein;
      carbohydrates = scaled.carbohydrates;
      fat = scaled.fat;
      fiber = scaled.fiber;
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
      fiber,
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
      origin: 'ai',
      reference,
    };
  });
}

const OFFLINE_NUMBER_WORDS: Record<string, number> = {
  a: 1,
  an: 1,
  one: 1,
  ek: 1,
  two: 2,
  do: 2,
  three: 3,
  teen: 3,
  four: 4,
  char: 4,
  five: 5,
  paanch: 5,
  six: 6,
  chhah: 6,
  half: 0.5,
  aadha: 0.5,
};

const UNIT_CONTAINERS = new Set([
  'bowl',
  'bowls',
  'katori',
  'cup',
  'cups',
  'glass',
  'glasses',
  'plate',
  'plates',
  'slice',
  'slices',
  'piece',
  'pieces',
  'tbsp',
  'tablespoon',
  'tablespoons',
  'tsp',
  'teaspoon',
  'teaspoons',
  'scoop',
  'scoops',
  'serving',
  'servings',
  'handful',
  'handfuls',
]);

const COUNTABLE_UNIT_NOUNS = new Set([
  'roti',
  'rotis',
  'chapati',
  'chapatis',
  'paratha',
  'parathas',
  'egg',
  'eggs',
  'idli',
  'idlis',
  'dosa',
  'dosas',
  'banana',
  'bananas',
  'apple',
  'apples',
]);

const PREPARATION_NOISE_REGEX =
  /\b(?:cooked|steamed|plain|fresh|hot|warm|cold|homestyle|bina chini|without sugar|no sugar|unsweetened|some|thoda)\b/gi;

function splitSpokenTranscriptClauses(transcript: string): {
  clauses: string[];
  hasCorrectionKeywords: boolean;
} {
  const hasCorrectionKeywords =
    /\b(?:actually|instead|make that|wait|nahi)\b/i.test(transcript);

  // If speaker corrected within an expression like "1 roti actually make that 2 rotis",
  // resolve trailing corrected phrase conservatively when isolated cleanly on commas/clauses.
  const rawParts = transcript
    .split(/(?:,|;|\+|\n|\b(?:and|with|aur|ke saath|plus)\b)/i)
    .map((p) => p.trim())
    .filter(Boolean);

  const clauses: string[] = [];
  for (const part of rawParts) {
    const correctionSplit = part.split(/\b(?:actually(?:\s+make\s+that)?|instead)\b/i);
    const chosen =
      correctionSplit.length > 1
        ? correctionSplit[correctionSplit.length - 1].trim()
        : part;
    if (chosen) {
      clauses.push(chosen);
    }
  }
  return { clauses, hasCorrectionKeywords };
}

function parseClausePortionAndQuery(clause: string): {
  quantity: number;
  unit: string;
  explicitGrams: number | null;
  foodQuery: string;
} {
  let working = clause.trim();
  let explicitGrams: number | null = null;
  let quantity = 1;
  let unit = 'serving';

  // Extract explicit gram or ml weights (e.g. "150g white rice", "100 gms oats", "200 ml milk")
  const weightMatch = working.match(/\b(\d+(?:\.\d+)?)\s*(g|gm|gms|gram|grams|ml)\b/i);
  if (weightMatch) {
    const val = Number(weightMatch[1]);
    if (Number.isFinite(val) && val > 0) {
      explicitGrams = val;
      quantity = val;
      unit = weightMatch[2].toLowerCase() === 'ml' ? 'ml' : 'g';
      working = `${working.slice(0, weightMatch.index ?? 0)} ${working.slice((weightMatch.index ?? 0) + weightMatch[0].length)}`.trim();
    }
  }

  // Extract leading numeric count or number word
  const tokens = working.split(/\s+/).filter(Boolean);
  if (tokens.length > 0) {
    const firstLower = tokens[0].toLowerCase();
    if (/^\d+(?:\.\d+)?$/.test(firstLower)) {
      const parsed = Number(firstLower);
      if (Number.isFinite(parsed) && parsed > 0) {
        if (explicitGrams === null) quantity = parsed;
        tokens.shift();
      }
    } else if (firstLower in OFFLINE_NUMBER_WORDS) {
      if (explicitGrams === null) quantity = OFFLINE_NUMBER_WORDS[firstLower];
      tokens.shift();
    }
  }

  // Strip container word if followed by optional "of" (e.g. "bowl of dal", "cup chai")
  if (tokens.length > 1) {
    const maybeUnit = tokens[0].toLowerCase();
    if (UNIT_CONTAINERS.has(maybeUnit)) {
      if (explicitGrams === null) unit = maybeUnit.replace(/s$/, '');
      tokens.shift();
      if (tokens[0]?.toLowerCase() === 'of') {
        tokens.shift();
      }
    } else if (COUNTABLE_UNIT_NOUNS.has(maybeUnit) && explicitGrams === null) {
      unit = maybeUnit.replace(/s$/, '');
    }
  }

  // Remove dangling filler "of"
  if (tokens[0]?.toLowerCase() === 'of') {
    tokens.shift();
  }

  const foodQuery = tokens.join(' ').replace(/\s+/g, ' ').trim();
  return { quantity, unit, explicitGrams, foodQuery: foodQuery || clause.trim() };
}

function singularizeToken(word: string): string {
  const lower = word.toLowerCase();
  if (lower.length > 4 && lower.endsWith('ies')) {
    return `${word.slice(0, -3)}y`;
  }
  if (lower.length > 3 && lower.endsWith('s') && !lower.endsWith('ss')) {
    return word.slice(0, -1);
  }
  return word;
}

function hasWholeWordTokenMatch(food: Food, query: string): boolean {
  const tokens = query
    .toLowerCase()
    .split(/\s+/)
    .map((t) => t.replace(/[^a-z0-9]/g, ''))
    .filter(Boolean);
  if (tokens.length === 0) return false;
  const haystacks = [food.name.toLowerCase(), ...food.aliases.map((a) => a.toLowerCase())];
  return tokens.every((tok) => {
    const escaped = tok.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`(?:^|[^a-z0-9])${escaped}(?:$|[^a-z0-9])`);
    return haystacks.some((h) => re.test(h));
  });
}

function findBestCatalogueMatches(
  availableFoods: readonly Food[],
  rawQuery: string,
): Food[] {
  const singularized = rawQuery
    .split(/\s+/)
    .map(singularizeToken)
    .join(' ')
    .trim();
  const strippedPrep = rawQuery
    .replace(PREPARATION_NOISE_REGEX, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  const strippedSingular = strippedPrep
    .split(/\s+/)
    .map(singularizeToken)
    .join(' ')
    .trim();

  // Prefer normalized singular/clean phrasing first, then fall back progressively.
  const candidatesToTry = Array.from(
    new Set(
      [singularized, rawQuery.trim(), strippedSingular, strippedPrep].filter(
        Boolean,
      ),
    ),
  );

  for (const q of candidatesToTry) {
    const found = searchFoods(availableFoods, q);
    if (found.length > 0) {
      // Preserve searchFoods ranking, gently promoting exact whole-word matches
      // (e.g. "Whole-wheat roti" ahead of partial prefix match "rotisserie chicken").
      const wholeWordHits = found.filter((f) => hasWholeWordTokenMatch(f, q));
      const rest = found.filter((f) => !hasWholeWordTokenMatch(f, q));
      return [...wholeWordHits, ...rest];
    }
  }
  return [];
}

function resolveOfflinePortionGrams(
  food: Food,
  quantity: number,
  unit: string,
  explicitGrams: number | null,
): { grams: number; note: string } {
  if (explicitGrams !== null && explicitGrams > 0) {
    return { grams: Math.round(explicitGrams * 10) / 10, note: 'Matched explicit spoken weight' };
  }

  const normUnit = unit.toLowerCase();
  if (food.commonServings && food.commonServings.length > 0) {
    const matchedServing = food.commonServings.find((s) =>
      s.description.toLowerCase().includes(normUnit),
    );
    if (matchedServing && matchedServing.grams > 0) {
      const g = Math.round(quantity * matchedServing.grams * 10) / 10;
      return {
        grams: g,
        note: `Offline match using catalogue serving "${matchedServing.description}" (${matchedServing.grams}g) — verify portion`,
      };
    }
  }

  if (food.servingGrams && food.servingGrams > 0) {
    const g = Math.round(quantity * food.servingGrams * 10) / 10;
    return {
      grams: g,
      note: `Offline match using catalogue serving (${food.servingGrams}g each) — verify portion`,
    };
  }

  const fallbackGrams = Math.round(quantity * 100 * 10) / 10;
  return {
    grams: fallbackGrams,
    note: `Offline reference weight (${fallbackGrams}g) — verify grams before saving`,
  };
}

/**
 * Deterministic offline voice transcript parser backed exclusively by local verified catalogue foods.
 * Never makes network calls and never invents or guesses missing macronutrients.
 */
export function matchVoiceTranscriptOffline(
  transcript: string,
  availableFoods: readonly Food[],
): OfflineVoiceMatchResult {
  const cleanedTranscript = transcript.trim();
  if (!cleanedTranscript) {
    return {
      transcript: '',
      summary: '',
      candidates: [],
      unmatchedClauses: [],
      warnings: ['Please enter a meal description to match against the local catalogue.'],
    };
  }

  const { clauses, hasCorrectionKeywords } = splitSpokenTranscriptClauses(cleanedTranscript);
  const warnings: string[] = [];
  if (hasCorrectionKeywords) {
    warnings.push(
      'Speech correction words detected offline — verify final items and portions before logging.',
    );
  }

  const candidates: MatchedVoiceFoodCandidate[] = [];
  const unmatchedClauses: string[] = [];
  const baseTs = Date.now();

  clauses.forEach((clause, index) => {
    const { quantity, unit, explicitGrams, foodQuery } = parseClausePortionAndQuery(clause);
    const matches = findBestCatalogueMatches(availableFoods, foodQuery);

    if (matches.length === 0) {
      unmatchedClauses.push(clause);
      warnings.push(
        `Could not match "${clause}" in the local catalogue; no nutrition was invented. Edit phrasing or add via Food Search.`,
      );
      return;
    }

    const topMatch = matches[0];
    const { grams, note } = resolveOfflinePortionGrams(topMatch, quantity, unit, explicitGrams);
    const scaled = scaleFoodNutrientsNullable(topMatch.nutrients, grams);

    const hasUnknownMacro =
      scaled.calories === null ||
      scaled.protein === null ||
      scaled.carbohydrates === null ||
      scaled.fat === null;
    if (hasUnknownMacro) {
      warnings.push(
        `${topMatch.name} has unreported (Unknown) nutrient fields in the catalogue; kept as Unknown without inventing values.`,
      );
    }

    const syntheticParsedPlaceholder: ParsedVoiceFoodItem = {
      food_description: topMatch.name,
      quantity,
      unit,
      preparation: topMatch.preparation,
      state: 'unspecified',
      estimated_grams: grams,
      calories: scaled.calories ?? 0,
      protein: scaled.protein ?? 0,
      carbohydrates: scaled.carbohydrates ?? 0,
      fat: scaled.fat ?? 0,
      confidence: 0.75,
      confidence_level: 'medium',
      alternatives: matches.slice(1, 4).map((m) => m.name),
      notes: note,
    };

    candidates.push({
      id: `voice-offline-${baseTs}-${index}`,
      stableEntryId: `voice-offline-entry-${baseTs}-${index}-${Math.random().toString(36).substring(2, 8)}`,
      originalParsedItem: syntheticParsedPlaceholder,
      food_name: topMatch.name,
      quantity,
      unit,
      estimated_grams: grams,
      calories: scaled.calories,
      protein: scaled.protein,
      carbohydrates: scaled.carbohydrates,
      fat: scaled.fat,
      fiber: scaled.fiber,
      state: 'unspecified',
      preparation: topMatch.preparation,
      notes: note,
      confidence: 0.75,
      confidence_level: 'medium',
      matchedCatalogueFood: topMatch,
      availableMatches: matches.slice(0, 8),
      sourceMode: 'catalogue',
      origin: 'offline_catalogue',
      reference: { ...topMatch.nutrients },
    });
  });

  const summary =
    candidates.length > 0
      ? `Matched ${candidates.length} local catalogue item${candidates.length === 1 ? '' : 's'} (review before saving)`
      : 'No local catalogue matches found';

  return {
    transcript: cleanedTranscript,
    summary,
    candidates,
    unmatchedClauses,
    warnings,
  };
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
      item.calories !== null &&
      (!Number.isFinite(item.calories) || item.calories < 0)
    ) {
      throw new RangeError(
        `Nutritional values for "${trimmedName}" must be non-negative finite numbers.`,
      );
    }
    if (
      item.protein !== null &&
      (!Number.isFinite(item.protein) || item.protein < 0)
    ) {
      throw new RangeError(
        `Nutritional values for "${trimmedName}" must be non-negative finite numbers.`,
      );
    }
    if (
      item.carbohydrates !== null &&
      (!Number.isFinite(item.carbohydrates) || item.carbohydrates < 0)
    ) {
      throw new RangeError(
        `Nutritional values for "${trimmedName}" must be non-negative finite numbers.`,
      );
    }
    if (item.fat !== null && (!Number.isFinite(item.fat) || item.fat < 0)) {
      throw new RangeError(
        `Nutritional values for "${trimmedName}" must be non-negative finite numbers.`,
      );
    }

    if (item.sourceMode === 'catalogue' && item.matchedCatalogueFood) {
      // Use verified or estimated catalogue entry (preserves null unknown macros via scaleNutrients)
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
      if (
        item.calories === null ||
        item.protein === null ||
        item.carbohydrates === null ||
        item.fat === null
      ) {
        throw new RangeError(
          `Nutritional values for "${trimmedName}" must be non-negative finite numbers.`,
        );
      }
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
        fiber: item.fiber ?? 0,
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
