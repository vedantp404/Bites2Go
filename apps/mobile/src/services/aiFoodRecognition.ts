import {
  AIResponseError,
  readAIResponse,
  validPhotoResponse,
  withResponseReference,
} from './aiResponse.ts';

/**
 * Client service for connecting the mobile app to the Bites2Go AI backend.
 */

// Pure TypeScript service (avoids direct React Native imports so it can run in Node unit tests).

export type UncertaintyInfo = {
  confidence_score: number;
  confidence_level: 'high' | 'medium' | 'low';
  notes?: string | null;
  alternatives: string[];
};

export type RecognizedFoodItem = {
  food_name: string;
  estimated_quantity: number;
  unit: string;
  estimated_grams: number;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  uncertainty: UncertaintyInfo;
};

export type FoodRecognitionResult = {
  success: boolean;
  summary: string;
  items: RecognizedFoodItem[];
  warnings: string[];
};

/**
 * Resolves the backend base URL.
 *
 * Priority:
 * 1. EXPO_PUBLIC_AI_BACKEND_URL, when configured.
 * 2. Android emulator's local development backend.
 * 3. localhost for non-production development.
 *
 * Production builds must provide the hosted HTTPS backend URL.
 */
export function getBackendBaseUrl(platform?: string): string {
  const configuredUrl = process.env.EXPO_PUBLIC_AI_BACKEND_URL?.trim();

  if (configuredUrl) {
    const normalizedUrl = configuredUrl.replace(/\/+$/, '');

    if (!/^https?:\/\//i.test(normalizedUrl)) {
      throw new Error(
        'Invalid AI backend URL. Use a complete URL beginning with https:// or http://.',
      );
    }

    return normalizedUrl;
  }

  // Prevent a standalone production app from silently using localhost.
  if (process.env.NODE_ENV === 'production') {
    throw new Error(
      'AI backend URL is not configured. Set EXPO_PUBLIC_AI_BACKEND_URL to the hosted HTTPS backend and rebuild the app.',
    );
  }

  const isAndroid =
    platform === 'android' ||
    (typeof process !== 'undefined' && process.env?.EXPO_OS === 'android');

  if (isAndroid) {
    return 'http://10.0.2.2:8000';
  }

  return 'http://localhost:8000';
}

/**
 * Safely checks whether the backend is available.
 */
export async function checkBackendHealth(): Promise<{
  available: boolean;
  aiConfigured: boolean;
  message?: string;
}> {
  let url: string;

  try {
    url = `${getBackendBaseUrl()}/health`;
  } catch (err: unknown) {
    return {
      available: false,
      aiConfigured: false,
      message: err instanceof Error ? err.message : String(err),
    };
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      return {
        available: false,
        aiConfigured: false,
        message: `Server error: HTTP ${response.status}`,
      };
    }

    const data = await response.json();

    return {
      available: true,
      aiConfigured: Boolean(data.ai_configured),
      message: data.service,
    };
  } catch (err: unknown) {
    const errorMsg =
      err instanceof Error
        ? err.name === 'AbortError'
          ? 'The backend health check timed out.'
          : err.message
        : String(err);

    return {
      available: false,
      aiConfigured: false,
      message: `Cannot connect to AI backend at ${url} (${errorMsg}). Manual search remains available offline.`,
    };
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Sends an image to the backend for AI food recognition.
 *
 * Uses the base64 endpoint when base64 image data is available.
 * Otherwise, sends the image using multipart FormData.
 */
class PhotoAnalysisError extends Error {}

export async function recognizeFoodFromImage(
  imageUri: string,
  base64Data?: string,
  opts?: { signal?: AbortSignal; timeoutMs?: number },
): Promise<FoodRecognitionResult> {
  const controller = new AbortController();
  const cancel = () => controller.abort();
  if (opts?.signal?.aborted) throw new Error('Photo analysis canceled.');
  opts?.signal?.addEventListener('abort', cancel, { once: true });
  const timeout = setTimeout(cancel, opts?.timeoutMs ?? 45000);
  try {
    const baseUrl = getBackendBaseUrl();
    const headers: Record<string, string> = { Accept: 'application/json' };
    let body: string | FormData;
    if (base64Data) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify({ image_base64: base64Data });
    } else {
      const filename = imageUri.split('/').pop() || 'photo.jpg';
      body = new FormData();
      body.append('file', {
        uri: imageUri,
        name: filename,
        type: /\.png$/i.test(filename) ? 'image/png' : 'image/jpeg',
      } as unknown as Blob);
    }
    const response = await fetch(
      `${baseUrl}/api/v1/recognize-food${base64Data ? '/base64' : ''}`,
      {
        method: 'POST',
        headers,
        body,
        signal: controller.signal,
      },
    );
    if (!response.ok) {
      const message =
        response.status === 429
          ? 'Photo analysis is busy. Please wait before retrying.'
          : response.status === 504
            ? 'Photo analysis timed out. Please retry or use Food Search.'
            : response.status === 413
              ? 'This photo is too large. Choose a smaller photo.'
              : response.status === 400 || response.status === 422
                ? 'This photo could not be read. Choose another photo.'
                : 'Photo analysis is temporarily unavailable. Please retry or use Food Search.';
      // Never display raw provider/proxy bodies, even when they contain a detail field.
      throw new PhotoAnalysisError(withResponseReference(message, response));
    }
    const result = await readAIResponse(response, validPhotoResponse);
    if (controller.signal.aborted)
      throw new DOMException('Aborted', 'AbortError');
    return result;
  } catch (error) {
    if (opts?.signal?.aborted) throw new Error('Photo analysis canceled.');
    if (controller.signal.aborted) {
      throw new Error(
        'Photo analysis timed out. Please retry or use Food Search.',
      );
    }
    if (error instanceof PhotoAnalysisError || error instanceof AIResponseError)
      throw error;
    // Android can reject fetch with a plain Error or AbortError independently of
    // our signal. Only our aborted signal proves that the client deadline fired.
    throw new Error(
      'Cannot reach photo analysis. Check your connection or use Food Search.',
    );
  } finally {
    clearTimeout(timeout);
    opts?.signal?.removeEventListener('abort', cancel);
  }
}

// Startup has a separate budget: Render free-instance wake-up can take about a minute.
export const PHOTO_READINESS_TIMEOUT_MS = 75_000;
export async function preparePhotoAnalysis(
  uri: string,
  base64?: string,
  opts?: {
    signal?: AbortSignal;
    readinessTimeoutMs?: number;
    timeoutMs?: number;
    onReady?: () => void;
  },
): Promise<FoodRecognitionResult> {
  const controller = new AbortController();
  const cancel = () => controller.abort();
  if (opts?.signal?.aborted) throw new Error('Photo analysis canceled.');
  opts?.signal?.addEventListener('abort', cancel, { once: true });
  const timer = setTimeout(
    cancel,
    opts?.readinessTimeoutMs ?? PHOTO_READINESS_TIMEOUT_MS,
  );
  try {
    while (true) {
      const response = await fetch(`${getBackendBaseUrl()}/health`, {
        signal: controller.signal,
        headers: { Accept: 'application/json' },
      });
      let ready = false;
      if (response.ok) {
        try {
          ready = (await response.json())?.status === 'ok';
        } catch (error) {
          if (!(error instanceof SyntaxError)) throw error;
        }
      } else if (![502, 503, 504].includes(response.status)) {
        throw new PhotoAnalysisError(
          'Photo service is unavailable. Please use Food Search or try later.',
        );
      }
      if (controller.signal.aborted) throw new Error('aborted');
      if (ready) break;
      // Retry readiness only, never an inference POST. Also handles proxy loading pages.
      await new Promise<void>((resolve, reject) => {
        const abort = () => {
          clearTimeout(wait);
          reject(new Error('aborted'));
        };
        const wait = setTimeout(() => {
          controller.signal.removeEventListener('abort', abort);
          resolve();
        }, 1500);
        controller.signal.addEventListener('abort', abort, { once: true });
        if (controller.signal.aborted) abort();
      });
    }
  } catch (error) {
    if (opts?.signal?.aborted) throw new Error('Photo analysis canceled.');
    if (controller.signal.aborted)
      throw new Error(
        'Photo service is taking too long to start. Please retry or use Food Search.',
      );
    if (error instanceof PhotoAnalysisError) throw error;
    throw new Error(
      'Cannot reach photo analysis. Check your connection or use Food Search.',
    );
  } finally {
    clearTimeout(timer);
    opts?.signal?.removeEventListener('abort', cancel);
  }
  if (opts?.signal?.aborted) throw new Error('Photo analysis canceled.');
  opts?.onReady?.();
  return recognizeFoodFromImage(uri, base64, opts);
}
