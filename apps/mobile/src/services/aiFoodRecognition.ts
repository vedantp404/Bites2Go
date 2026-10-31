/**
 * Client service for connecting mobile app to local Gemini AI backend.
 */

// Pure TypeScript service (avoids direct react-native imports so it can run in Node unit tests)

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
 * - Android Emulator routes to 10.0.2.2 to reach host loopback.
 * - iOS Simulator and Web route to localhost:8000.
 * - Can be overridden via EXPO_PUBLIC_AI_BACKEND_URL for physical LAN devices.
 */
export function getBackendBaseUrl(platform?: string): string {
  if (process.env.EXPO_PUBLIC_AI_BACKEND_URL) {
    return process.env.EXPO_PUBLIC_AI_BACKEND_URL.replace(/\/+$/, '');
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
 * Safe ping to verify backend availability.
 */
export async function checkBackendHealth(): Promise<{
  available: boolean;
  aiConfigured: boolean;
  message?: string;
}> {
  const url = `${getBackendBaseUrl()}/health`;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);
    const response = await fetch(url, {
      credentials: 'omit',
      signal: controller.signal,
    });
    clearTimeout(timeout);

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
    const errorMsg = err instanceof Error ? err.message : String(err);
    return {
      available: false,
      aiConfigured: false,
      message: `Cannot connect to AI backend at ${url} (${errorMsg}). Manual search remains available offline.`,
    };
  }
}

/**
 * Send an image to the local backend for Gemini food recognition.
 */
export async function recognizeFoodFromImage(
  imageUri: string,
  base64Data?: string,
): Promise<FoodRecognitionResult> {
  const baseUrl = getBackendBaseUrl();

  // If base64 data is already available from ImagePicker, prefer the base64 route
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
        body: JSON.stringify({ image_base64: base64Data }),
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
        throw new Error(detail);
      }

      return (await response.json()) as FoodRecognitionResult;
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') {
        throw new Error(
          'AI recognition request timed out. Please check your connection and try again.',
        );
      }
      throw err;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // Fallback to multipart FormData
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
        } else if (errorJson?.detail?.message) {
          detail = errorJson.detail.message;
        }
      } catch {
        // use default detail
      }
      throw new Error(detail);
    }

    return (await response.json()) as FoodRecognitionResult;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error(
        'AI recognition request timed out. Please check your connection and try again.',
      );
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}
