/** Validate the network boundary before AI output reaches editable meal state. */
import type { FoodRecognitionResult } from './aiFoodRecognition.ts';
import type { VoiceMealParseResponse } from './voiceFoodLogging.ts';

export function responseRequestId(response: Response): string | undefined {
  const value = response.headers?.get?.('X-Request-ID');
  return value && /^[a-f0-9]{32}$/i.test(value) ? value : undefined;
}

export class AIResponseError extends Error {
  readonly requestId?: string;
  constructor(response: Response) {
    const requestId = responseRequestId(response);
    super(
      'The AI service returned an invalid result. Please retry or use Food Search.' +
        (requestId ? ` Reference: ${requestId}.` : ''),
    );
    this.name = 'AIResponseError';
    this.requestId = requestId;
  }
}

type RecordValue = Record<string, unknown>;
const record = (v: unknown): v is RecordValue =>
  !!v && typeof v === 'object' && !Array.isArray(v);
const text = (v: unknown): v is string => typeof v === 'string';
const strings = (v: unknown): v is string[] =>
  Array.isArray(v) && v.every(text);
const nonnegative = (v: unknown): v is number =>
  typeof v === 'number' && Number.isFinite(v) && v >= 0;
const positive = (v: unknown): v is number => nonnegative(v) && v > 0;
const confidence = (v: unknown) => nonnegative(v) && v <= 1;
const level = (v: unknown) => ['high', 'medium', 'low'].includes(v as string);
const optionalText = (v: unknown) => v == null || text(v);
const nutrients = ['calories', 'protein', 'carbohydrates', 'fat'];

export function validVoiceResponse(v: unknown): v is VoiceMealParseResponse {
  return (
    record(v) &&
    v.success === true &&
    text(v.transcript) &&
    text(v.summary) &&
    strings(v.warnings) &&
    strings(v.clarifying_questions) &&
    Array.isArray(v.items) &&
    v.items.every(
      (item: unknown) =>
        record(item) &&
        text(item.food_description) &&
        !!item.food_description.trim() &&
        positive(item.quantity) &&
        text(item.unit) &&
        !!item.unit.trim() &&
        ['raw', 'cooked', 'unspecified'].includes(item.state as string) &&
        (item.estimated_grams === null || positive(item.estimated_grams)) &&
        nutrients.every(
          (key) => item[key] === null || nonnegative(item[key]),
        ) &&
        confidence(item.confidence) &&
        level(item.confidence_level) &&
        strings(item.alternatives) &&
        optionalText(item.preparation) &&
        optionalText(item.notes) &&
        (item.modifiers === undefined || strings(item.modifiers)) &&
        (item.portion_specified === undefined ||
          typeof item.portion_specified === 'boolean'),
    )
  );
}

export function validPhotoResponse(v: unknown): v is FoodRecognitionResult {
  return (
    record(v) &&
    v.success === true &&
    text(v.summary) &&
    strings(v.warnings) &&
    Array.isArray(v.items) &&
    v.items.every(
      (item: unknown) =>
        record(item) &&
        text(item.food_name) &&
        !!item.food_name.trim() &&
        nonnegative(item.estimated_quantity) &&
        text(item.unit) &&
        !!item.unit.trim() &&
        positive(item.estimated_grams) &&
        nutrients.every((key) => nonnegative(item[key])) &&
        record(item.uncertainty) &&
        confidence(item.uncertainty.confidence_score) &&
        level(item.uncertainty.confidence_level) &&
        strings(item.uncertainty.alternatives) &&
        optionalText(item.uncertainty.notes),
    )
  );
}

export async function readAIResponse<T>(
  response: Response,
  valid: (v: unknown) => v is T,
): Promise<T> {
  let value: unknown;
  try {
    value = await response.json();
  } catch (error) {
    // Body timeouts and cancellation still belong to their existing transport handlers.
    if (!(error instanceof SyntaxError)) throw error;
    throw new AIResponseError(response);
  }
  if (!valid(value)) throw new AIResponseError(response);
  return value;
}

export function withResponseReference(
  message: string,
  response: Response,
): string {
  const id = responseRequestId(response);
  return id ? `${message} Reference: ${id}.` : message;
}
