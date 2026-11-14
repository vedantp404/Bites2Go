import {
  AIResponseError,
  readAIResponse,
  validVoiceResponse,
  responseRequestId,
  withResponseReference,
} from './aiResponse.ts';

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

export const MAX_AUDIO_DURATION_MS = 90_000;
export const MAX_AUDIO_FILE_BYTES = 10 * 1024 * 1024;
export const MIN_AUDIO_DURATION_MS = 400;
export const MIN_AUDIO_FILE_BYTES = 512;
export const AUDIO_UPLOAD_TIMEOUT_MS = 45_000;

export type ParsedVoiceFoodItem = {
  food_description: string;
  quantity: number;
  unit: string;
  preparation?: string | null;
  modifiers?: string[];
  state: 'raw' | 'cooked' | 'unspecified';
  portion_specified?: boolean;
  estimated_grams: number | null;
  calories: number | null;
  protein: number | null;
  carbohydrates: number | null;
  fat: number | null;
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
  estimated_grams: number | null;
  calories: number | null;
  protein: number | null;
  carbohydrates: number | null;
  fat: number | null;
  fiber?: number | null;
  state: 'raw' | 'cooked' | 'unspecified';
  preparation: string;
  modifiers?: string[];
  portionSpecified?: boolean;
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
  requestId?: string;
  status?: number;
  retryAfterSeconds?: number;
  errorCategory?: string;

  constructor(
    message: string,
    opts?: {
      requestId?: string;
      status?: number;
      retryAfterSeconds?: number;
      errorCategory?: string;
    },
  ) {
    super(message);
    this.name = 'VoiceCloudError';
    this.requestId = opts?.requestId;
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

export function validateRecordedAudioMetadata(input: {
  uri?: string | null;
  durationMillis: number;
  sizeBytes?: number | null;
}): { valid: boolean; error?: string } {
  const cleanUri = input.uri?.trim() || '';
  if (!cleanUri) {
    return {
      valid: false,
      error: 'No audio recording was captured. Tap Speak and try again.',
    };
  }
  if (
    !Number.isFinite(input.durationMillis) ||
    input.durationMillis < MIN_AUDIO_DURATION_MS
  ) {
    return {
      valid: false,
      error:
        'Recording was too short. Hold and speak your meal clearly for at least 1 second.',
    };
  }
  if (input.durationMillis > MAX_AUDIO_DURATION_MS + 2000) {
    return {
      valid: false,
      error:
        'Recording exceeded the 90-second limit. Please split very long meals or record a shorter description.',
    };
  }
  if (input.sizeBytes !== null && input.sizeBytes !== undefined) {
    if (input.sizeBytes < MIN_AUDIO_FILE_BYTES) {
      return {
        valid: false,
        error:
          'Captured audio file appears empty. Check your microphone and try again.',
      };
    }
    if (input.sizeBytes > MAX_AUDIO_FILE_BYTES) {
      return {
        valid: false,
        error:
          'Audio recording is too large to upload (10 MB max). Please record a shorter clip.',
      };
    }
  }
  return { valid: true };
}

export function inferAudioMimeAndName(audioUri: string): {
  filename: string;
  mimeType: string;
} {
  const rawName = audioUri.split('/').pop() || 'meal-voice.m4a';
  const cleanName = rawName.split('?')[0] || 'meal-voice.m4a';
  const match = /\.(\w+)$/.exec(cleanName);
  const ext = match ? match[1].toLowerCase() : 'm4a';
  switch (ext) {
    case 'mp4':
      return { filename: cleanName, mimeType: 'audio/mp4' };
    case 'aac':
      return { filename: cleanName, mimeType: 'audio/aac' };
    case 'wav':
      return { filename: cleanName, mimeType: 'audio/wav' };
    case 'mp3':
      return { filename: cleanName, mimeType: 'audio/mpeg' };
    case 'ogg':
    case 'opus':
      return { filename: cleanName, mimeType: 'audio/ogg' };
    case 'webm':
      return { filename: cleanName, mimeType: 'audio/webm' };
    case 'flac':
      return { filename: cleanName, mimeType: 'audio/flac' };
    case 'm4a':
    default:
      return {
        filename: cleanName.endsWith(`.${ext}`) ? cleanName : 'meal-voice.m4a',
        mimeType: 'audio/m4a',
      };
  }
}

export function sanitizeVoiceUserMessage(
  rawDetail?: string,
  status?: number,
): string {
  const trimmed = (rawDetail || '').trim();
  const hasRawJsonOrTechnicalNoise =
    !trimmed ||
    trimmed.startsWith('{') ||
    trimmed.startsWith('[') ||
    /^(?:Error|HTTP)\s+\d{3}\b/i.test(trimmed) ||
    /\bHTTP\s*\d{3}\b/i.test(trimmed) ||
    /\b(?:nvidia\/|dots-studio\/|openrouter\/|gemini-[\d.]+|traceback|syntaxerror|validationerror)\b/i.test(
      trimmed,
    );

  if (!hasRawJsonOrTechnicalNoise) {
    return trimmed.replace(/\bOpenRouter\s+/gi, '');
  }

  if (status === 429) {
    return 'Voice AI reached temporary rate or daily quota limits. Wait briefly to retry, edit your description below, or open Food Search.';
  }
  if (status === 504) {
    return 'Voice meal analysis timed out. You can retry the recording, edit text below, or open Food Search.';
  }
  if (status === 413) {
    return 'Audio recording exceeded the maximum size limit. Record a shorter clip or open Food Search.';
  }
  if (status === 502 || status === 503) {
    return 'Could not interpret that meal clearly right now. You can retry, edit your description below, or open Food Search.';
  }
  return 'Unable to reach voice AI right now. You can retry, type your meal below, or open Food Search.';
}

/**
 * Upload recorded meal audio securely over HTTPS/HTTP to FastAPI for direct audio-native AI interpretation.
 */
export async function parseVoiceAudio(
  audioUri: string,
  mealContext?: string,
  loggedDate?: string,
  opts?: { signal?: AbortSignal; timeoutMs?: number },
): Promise<VoiceMealParseResponse> {
  const cleanUri = audioUri.trim();
  if (!cleanUri) {
    throw new VoiceCloudError('No audio recording found to analyze.', {
      status: 400,
      errorCategory: 'missing_audio',
    });
  }

  const baseUrl = getBackendBaseUrl();
  const url = `${baseUrl}/api/v1/parse-voice-audio`;
  const { filename, mimeType } = inferAudioMimeAndName(cleanUri);

  const formData = new FormData();
  formData.append('file', {
    uri: cleanUri,
    name: filename,
    type: mimeType,
  } as unknown as Blob);
  if (mealContext?.trim()) {
    formData.append('meal_context', mealContext.trim());
  }
  if (loggedDate?.trim()) {
    formData.append('logged_date', loggedDate.trim());
  }

  const controller = new AbortController();
  const timeoutMs = opts?.timeoutMs ?? AUDIO_UPLOAD_TIMEOUT_MS;
  let timedOut = false;
  const timeoutId = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  const onExternalAbort = () => controller.abort();
  if (opts?.signal) {
    if (opts.signal.aborted) {
      clearTimeout(timeoutId);
      throw new VoiceCloudError('Audio analysis canceled.', {
        errorCategory: 'upload_canceled',
      });
    }
    opts.signal.addEventListener('abort', onExternalAbort, { once: true });
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
      body: formData,
      signal: controller.signal,
    });

    if (!response.ok) {
      let rawDetail = '';
      try {
        const errorJson = await response.json();
        if (typeof errorJson?.detail === 'string') {
          rawDetail = errorJson.detail;
        } else if (typeof errorJson?.detail?.message === 'string') {
          rawDetail = errorJson.detail.message;
        }
      } catch {
        // ignore JSON parse failure on non-JSON proxy errors
      }
      const rawRetryAfter = response.headers?.get?.('Retry-After');
      const retryAfterNum = rawRetryAfter ? Number(rawRetryAfter) : NaN;
      const errorCategory =
        response.headers?.get?.('X-Error-Category') ?? undefined;
      throw new VoiceCloudError(
        withResponseReference(
          sanitizeVoiceUserMessage(rawDetail, response.status),
          response,
        ),
        {
          requestId: responseRequestId(response),
          status: response.status,
          retryAfterSeconds: Number.isFinite(retryAfterNum)
            ? retryAfterNum
            : undefined,
          errorCategory,
        },
      );
    }

    return await readAIResponse(response, validVoiceResponse);
  } catch (err: unknown) {
    if (err instanceof AIResponseError) {
      throw new VoiceCloudError(err.message, {
        requestId: err.requestId,
        errorCategory: 'invalid_response',
      });
    }
    if (err instanceof VoiceCloudError) {
      throw err;
    }
    if (opts?.signal?.aborted) {
      throw new VoiceCloudError('Audio analysis canceled.', {
        errorCategory: 'upload_canceled',
      });
    }
    if (err instanceof Error && (err.name === 'AbortError' || timedOut)) {
      throw new VoiceCloudError(
        'Voice meal analysis timed out. You can retry the recording, edit text manually, or open Food Search.',
        { status: 504, errorCategory: 'timeout' },
      );
    }
    throw new VoiceCloudError(sanitizeVoiceUserMessage(), {
      errorCategory: 'network_error',
    });
  } finally {
    clearTimeout(timeoutId);
    opts?.signal?.removeEventListener('abort', onExternalAbort);
  }
}

/**
 * Send voice transcript to FastAPI backend for natural language food extraction.
 */
export async function parseVoiceMeal(
  transcript: string,
  mealContext?: string,
  loggedDate?: string,
  opts?: { signal?: AbortSignal; timeoutMs?: number },
): Promise<VoiceMealParseResponse> {
  const cleaned = transcript.trim();
  if (!cleaned) {
    throw new Error('Please speak or type a food description.');
  }

  const baseUrl = getBackendBaseUrl();
  const url = `${baseUrl}/api/v1/parse-voice-meal`;
  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(),
    opts?.timeoutMs ?? 40000,
  );
  const onExternalAbort = () => controller.abort();
  if (opts?.signal) {
    if (opts.signal.aborted) {
      clearTimeout(timeoutId);
      throw new VoiceCloudError('Voice analysis canceled.', {
        errorCategory: 'upload_canceled',
      });
    }
    opts.signal.addEventListener('abort', onExternalAbort, { once: true });
  }

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
      let detail = '';
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
      const errorCategory =
        response.headers?.get?.('X-Error-Category') ?? undefined;
      throw new VoiceCloudError(
        withResponseReference(
          sanitizeVoiceUserMessage(detail, response.status),
          response,
        ),
        {
          requestId: responseRequestId(response),
          status: response.status,
          retryAfterSeconds: Number.isFinite(retryAfterNum)
            ? retryAfterNum
            : undefined,
          errorCategory,
        },
      );
    }

    return await readAIResponse(response, validVoiceResponse);
  } catch (err: unknown) {
    if (err instanceof AIResponseError) {
      throw new VoiceCloudError(err.message, {
        requestId: err.requestId,
        errorCategory: 'invalid_response',
      });
    }
    if (err instanceof VoiceCloudError) {
      throw err;
    }
    if (opts?.signal?.aborted) {
      throw new VoiceCloudError('Voice analysis canceled.', {
        errorCategory: 'upload_canceled',
      });
    }
    if (err instanceof Error && err.name === 'AbortError') {
      throw new VoiceCloudError(
        'Voice meal analysis timed out. Please retry or open Food Search.',
        { status: 504, errorCategory: 'timeout' },
      );
    }
    throw new VoiceCloudError(sanitizeVoiceUserMessage(), {
      errorCategory: 'network_error',
    });
  } finally {
    clearTimeout(timeoutId);
    opts?.signal?.removeEventListener('abort', onExternalAbort);
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
function deriveAIReferencePer100g(
  item: ParsedVoiceFoodItem,
  grams: number | null,
): FoodNutrients {
  if (!grams || grams <= 0) {
    return {
      calories: null,
      protein: null,
      carbs: null,
      fat: null,
      fiber: null,
    };
  }
  const factor = 100 / grams;
  return {
    calories:
      item.calories !== null && Number.isFinite(item.calories)
        ? Math.round(item.calories * factor * 1000) / 1000
        : null,
    protein:
      item.protein !== null && Number.isFinite(item.protein)
        ? Math.round(item.protein * factor * 1000) / 1000
        : null,
    carbs:
      item.carbohydrates !== null && Number.isFinite(item.carbohydrates)
        ? Math.round(item.carbohydrates * factor * 1000) / 1000
        : null,
    fat:
      item.fat !== null && Number.isFinite(item.fat)
        ? Math.round(item.fat * factor * 1000) / 1000
        : null,
    fiber: 0,
  };
}

/**
 * Match parsed voice food items to the existing 1,411-food unified catalogue,
 * preserving dish specificity, modifiers, uncertainty, and unknown nulls.
 */
export function matchVoiceItemsToCatalogue(
  items: ParsedVoiceFoodItem[],
  availableFoods: readonly Food[],
): MatchedVoiceFoodCandidate[] {
  return items.map((item, index) => {
    const portionSpecified =
      item.portion_specified !== false &&
      item.estimated_grams !== null &&
      Number.isFinite(item.estimated_grams) &&
      item.estimated_grams > 0;
    const rawGrams: number | null = portionSpecified
      ? item.estimated_grams
      : null;
    const query = item.food_description.trim();
    const queryLower = query.toLowerCase();
    const modifiers = Array.isArray(item.modifiers)
      ? item.modifiers.map((m) => m.trim()).filter(Boolean)
      : [];

    // Search existing catalogue using searchFoods (handles dataset-first ranking)
    const matches = searchFoods(availableFoods, query);

    // If query has 0-4 matches, also search alternatives provided by Gemini
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

    // Only auto-select catalogue when the catalogue food is at least as specific as the spoken dish;
    // never overwrite "Sourdough toast" with generic "Toast" or "Whey protein powder" with "Protein".
    const isCloseMatch =
      topMatch !== null &&
      (topMatch.name.toLowerCase() === queryLower ||
        topMatch.name.toLowerCase().includes(queryLower));

    const sourceMode: 'catalogue' | 'ai' = isCloseMatch ? 'catalogue' : 'ai';

    let calories: number | null = rawGrams !== null ? item.calories : null;
    let protein: number | null = rawGrams !== null ? item.protein : null;
    let carbohydrates: number | null =
      rawGrams !== null ? item.carbohydrates : null;
    let fat: number | null = rawGrams !== null ? item.fat : null;
    let fiber: number | null = rawGrams !== null ? 0 : null;
    let reference: FoodNutrients;

    if (sourceMode === 'catalogue' && topMatch) {
      reference = { ...topMatch.nutrients };
      if (rawGrams !== null) {
        const scaled = scaleFoodNutrientsNullable(topMatch.nutrients, rawGrams);
        calories = scaled.calories;
        protein = scaled.protein;
        carbohydrates = scaled.carbohydrates;
        fat = scaled.fat;
        fiber = scaled.fiber;
      } else {
        calories = null;
        protein = null;
        carbohydrates = null;
        fat = null;
        fiber = null;
      }
    } else {
      reference = deriveAIReferencePer100g(item, rawGrams);
    }

    const baseNoteParts: string[] = [];
    if (modifiers.length > 0) {
      baseNoteParts.push(`Includes ${modifiers.join(', ')}`);
    }
    if (item.notes?.trim()) {
      baseNoteParts.push(item.notes.trim());
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
      modifiers,
      portionSpecified,
      notes: baseNoteParts.join(' · '),
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
    const correctionSplit = part.split(
      /\b(?:actually(?:\s+make\s+that)?|instead)\b/i,
    );
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
  const weightMatch = working.match(
    /\b(\d+(?:\.\d+)?)\s*(g|gm|gms|gram|grams|ml)\b/i,
  );
  if (weightMatch) {
    const val = Number(weightMatch[1]);
    if (Number.isFinite(val) && val > 0) {
      explicitGrams = val;
      quantity = val;
      unit = weightMatch[2].toLowerCase() === 'ml' ? 'ml' : 'g';
      working =
        `${working.slice(0, weightMatch.index ?? 0)} ${working.slice((weightMatch.index ?? 0) + weightMatch[0].length)}`.trim();
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
  return {
    quantity,
    unit,
    explicitGrams,
    foodQuery: foodQuery || clause.trim(),
  };
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
  const haystacks = [
    food.name.toLowerCase(),
    ...food.aliases.map((a) => a.toLowerCase()),
  ];
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
    return {
      grams: Math.round(explicitGrams * 10) / 10,
      note: 'Matched explicit spoken weight',
    };
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
      warnings: [
        'Please enter a meal description to match against the local catalogue.',
      ],
    };
  }

  const { clauses, hasCorrectionKeywords } =
    splitSpokenTranscriptClauses(cleanedTranscript);
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
    const { quantity, unit, explicitGrams, foodQuery } =
      parseClausePortionAndQuery(clause);
    const matches = findBestCatalogueMatches(availableFoods, foodQuery);

    if (matches.length === 0) {
      unmatchedClauses.push(clause);
      warnings.push(
        `Could not match "${clause}" in the local catalogue; no nutrition was invented. Edit phrasing or add via Food Search.`,
      );
      return;
    }

    const topMatch = matches[0];
    const { grams, note } = resolveOfflinePortionGrams(
      topMatch,
      quantity,
      unit,
      explicitGrams,
    );
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
      modifiers: [],
      portionSpecified: true,
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
    if (
      item.estimated_grams === null ||
      !Number.isFinite(item.estimated_grams) ||
      item.estimated_grams <= 0
    ) {
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
      const basePrep = item.preparation?.trim() || 'Voice logged meal';
      const modSuffix =
        item.modifiers && item.modifiers.length > 0
          ? ` (${item.modifiers.join(', ')})`
          : '';
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
        fiber: item.fiber === undefined ? 0 : item.fiber,
        preparation: `${basePrep}${modSuffix}`.slice(0, 120),
        source: 'Gemini AI Voice Parser',
        now,
      });
      assertEntry(entry);
      entries.push(entry);
    }
  }

  return entries;
}
