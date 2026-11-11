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
export async function recognizeFoodFromImage(
  imageUri: string,
  base64Data?: string,
): Promise<FoodRecognitionResult> {
  const baseUrl = getBackendBaseUrl();

  // Prefer the base64 endpoint when image data is already available.
  if (base64Data && base64Data.length > 0) {
    const url = `${baseUrl}/api/v1/recognize-food/base64`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 45000);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          image_base64: base64Data,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        let detail = `Error ${response.status}`;

        try {
          const errorJson = await response.json();

          if (typeof errorJson?.detail === 'string') {
            detail = errorJson.detail;
          } else if (typeof errorJson?.detail?.message === 'string') {
            detail = errorJson.detail.message;
          }
        } catch {
          // Retain the default error message.
        }

        throw new Error(detail);
      }

      return (await response.json()) as FoodRecognitionResult;
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') {
        throw new Error(
          'AI recognition request timed out. Check your internet connection and try again.',
        );
      }

      throw err;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // Fallback: upload the image as multipart FormData.
  const url = `${baseUrl}/api/v1/recognize-food`;
  const formData = new FormData();

  const filename = imageUri.split('/').pop() || 'photo.jpg';
  const match = /\.(\w+)$/.exec(filename);
  const ext = match ? match[1].toLowerCase() : 'jpg';
  const mimeType = ext === 'png' ? 'image/png' : 'image/jpeg';

  formData.append('file', {
    uri: imageUri,
    name: filename,
    type: mimeType,
  } as unknown as Blob);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 45000);

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
      let detail = `Error ${response.status}`;

      try {
        const errorJson = await response.json();

        if (typeof errorJson?.detail === 'string') {
          detail = errorJson.detail;
        } else if (typeof errorJson?.detail?.message === 'string') {
          detail = errorJson.detail.message;
        }
      } catch {
        // Retain the default error message.
      }

      throw new Error(detail);
    }

    return (await response.json()) as FoodRecognitionResult;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error(
        'AI recognition request timed out. Check your internet connection and try again.',
      );
    }

    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}
