import test from 'node:test';
import assert from 'node:assert/strict';
import {
  getBackendBaseUrl,
  checkBackendHealth,
  recognizeFoodFromImage,
} from '../src/services/aiFoodRecognition.ts';
import {
  parseVoiceAudio,
  parseVoiceMeal,
  sanitizeVoiceUserMessage,
  VoiceCloudError,
} from '../src/services/voiceFoodLogging.ts';

test('getBackendBaseUrl: resolves default and custom URL values', () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  const originalNodeEnv = process.env.NODE_ENV;
  try {
    delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    process.env.NODE_ENV = 'test';
    const defaultUrl = getBackendBaseUrl();
    assert.ok(defaultUrl.startsWith('http://'));

    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'http://192.168.1.50:8000/';
    assert.equal(getBackendBaseUrl(), 'http://192.168.1.50:8000');
  } finally {
    if (originalNodeEnv !== undefined) {
      process.env.NODE_ENV = originalNodeEnv;
    } else {
      delete process.env.NODE_ENV;
    }
    if (originalEnv) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});

test('checkBackendHealth: returns error message safely when server unreachable without crashing', async () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  try {
    // Point to an unreachable port on purpose
    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'http://127.0.0.1:59999';
    const result = await checkBackendHealth();
    assert.equal(result.available, false);
    assert.equal(result.aiConfigured, false);
    assert.ok(
      result.message &&
        result.message.includes('Manual search remains available'),
    );
  } finally {
    if (originalEnv) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});

test('recognizeFoodFromImage: handles fetch timeout and abort signal cleanly', async () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  const originalFetch = globalThis.fetch;
  try {
    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'http://127.0.0.1:8000';
    // Mock fetch that simulates AbortError
    globalThis.fetch = async () => {
      const err = new Error('The operation was aborted');
      err.name = 'AbortError';
      throw err;
    };

    await assert.rejects(async () => {
      await recognizeFoodFromImage('file:///test.jpg', 'fakeBase64');
    }, /timed out/i);
  } finally {
    globalThis.fetch = originalFetch;
    if (originalEnv) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});

test('recognizeFoodFromImage: parses structured 504 and 503 error details from backend', async () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  const originalFetch = globalThis.fetch;
  try {
    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'http://127.0.0.1:8000';

    // Mock 504 Gateway Timeout
    globalThis.fetch = async () => ({
      ok: false,
      status: 504,
      json: async () => ({
        detail:
          'The AI food recognition service timed out after multiple attempts. Please try again.',
      }),
    });

    await assert.rejects(
      async () => {
        await recognizeFoodFromImage('file:///test.jpg', 'fakeBase64');
      },
      (err) => {
        assert.ok(err instanceof Error && err.message.includes('timed out'));
        return true;
      },
    );

    // Mock 503 Service Unavailable
    globalThis.fetch = async () => ({
      ok: false,
      status: 503,
      json: async () => ({
        detail:
          'The AI food recognition service is temporarily overloaded or unavailable. Please try again in a few moments.',
      }),
    });

    await assert.rejects(
      async () => {
        await recognizeFoodFromImage('file:///test.jpg', 'fakeBase64');
      },
      (err) => {
        assert.ok(
          err instanceof Error &&
            err.message.includes('temporarily unavailable'),
        );
        return true;
      },
    );
  } finally {
    globalThis.fetch = originalFetch;
    if (originalEnv) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});

test('parseVoiceMeal: parses structured 504 and 503 error details from backend', async () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  const originalFetch = globalThis.fetch;
  try {
    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'http://127.0.0.1:8000';

    // Mock 504 Gateway Timeout
    globalThis.fetch = async () => ({
      ok: false,
      status: 504,
      json: async () => ({
        detail:
          'The AI voice parsing service timed out after multiple attempts. Please try again.',
      }),
    });

    await assert.rejects(
      async () => {
        await parseVoiceMeal('a bowl of dal');
      },
      (err) => {
        assert.ok(
          err instanceof Error &&
            err.message.includes('timed out after multiple attempts'),
        );
        return true;
      },
    );

    // Mock 503 Service Unavailable
    globalThis.fetch = async () => ({
      ok: false,
      status: 503,
      json: async () => ({
        detail:
          'The AI voice parsing service is temporarily overloaded or unavailable. Please try again in a few moments.',
      }),
    });

    await assert.rejects(
      async () => {
        await parseVoiceMeal('two rotis');
      },
      (err) => {
        assert.ok(
          err instanceof Error &&
            err.message.includes('temporarily overloaded or unavailable'),
        );
        return true;
      },
    );
    // Mock 429 Too Many Requests with Retry-After and X-Error-Category headers
    const mockHeaders = new Headers({
      'Retry-After': '25',
      'X-Error-Category': 'daily_quota_exhausted',
    });
    globalThis.fetch = async () => ({
      ok: false,
      status: 429,
      headers: mockHeaders,
      json: async () => ({
        detail: 'OpenRouter free-tier daily quota exhausted.',
      }),
    });

    await assert.rejects(
      async () => {
        await parseVoiceMeal('two rotis and dal');
      },
      (err) => {
        assert.ok(err instanceof VoiceCloudError);
        assert.equal(err.status, 429);
        assert.equal(err.retryAfterSeconds, 25);
        assert.equal(err.errorCategory, 'daily_quota_exhausted');
        assert.ok(err.message.includes('daily quota exhausted'));
        return true;
      },
    );
  } finally {
    globalThis.fetch = originalFetch;
    if (originalEnv) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});

test('getBackendBaseUrl & checkBackendHealth: enforce production URL config and scheme validation', async () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  const originalNodeEnv = process.env.NODE_ENV;
  try {
    process.env.NODE_ENV = 'production';
    delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;

    assert.throws(
      () => getBackendBaseUrl('android'),
      /AI backend URL is not configured/,
    );

    const missingHealth = await checkBackendHealth();
    assert.equal(missingHealth.available, false);
    assert.equal(missingHealth.aiConfigured, false);
    assert.ok(
      missingHealth.message?.includes('AI backend URL is not configured'),
    );

    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'bites2go-api.onrender.com';
    assert.throws(() => getBackendBaseUrl('android'), /Invalid AI backend URL/);

    process.env.EXPO_PUBLIC_AI_BACKEND_URL =
      ' https://bites2go-api.onrender.com/ ';
    assert.equal(
      getBackendBaseUrl('android'),
      'https://bites2go-api.onrender.com',
    );
  } finally {
    if (originalNodeEnv !== undefined) {
      process.env.NODE_ENV = originalNodeEnv;
    } else {
      delete process.env.NODE_ENV;
    }
    if (originalEnv !== undefined) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});

test('parseVoiceAudio: uploads audio, handles cancellation, sanitizes raw errors/models, and maps 429/504 cleanly', async () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  const originalFetch = globalThis.fetch;
  try {
    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'http://127.0.0.1:8000';

    // Successful multipart audio upload
    let capturedMethod = '';
    let capturedUrl = '';
    globalThis.fetch = async (url, init) => {
      capturedUrl = String(url);
      capturedMethod = String(init?.method || '');
      assert.ok(init?.body instanceof FormData);
      return {
        ok: true,
        status: 200,
        json: async () => ({
          success: true,
          transcript: 'Two rotis, no wait, three rotis and dal',
          summary: '3 rotis and dal',
          items: [
            {
              food_description: 'Whole wheat roti',
              quantity: 3,
              unit: 'roti',
              state: 'cooked',
              modifiers: [],
              portion_specified: true,
              estimated_grams: 105,
              calories: 270,
              protein: 9,
              carbohydrates: 54,
              fat: 2.1,
              confidence: 0.91,
              confidence_level: 'high',
              alternatives: [],
            },
          ],
          warnings: ['Corrected rotis from 2 to 3'],
          clarifying_questions: [],
        }),
      };
    };

    const okRes = await parseVoiceAudio(
      'file:///cache/meal.m4a',
      'Dinner',
      '2026-11-12',
    );
    assert.equal(capturedMethod, 'POST');
    assert.ok(capturedUrl.endsWith('/api/v1/parse-voice-audio'));
    assert.equal(okRes.items[0].quantity, 3);

    // Caller cancellation cleanly aborts upload
    const abortController = new AbortController();
    abortController.abort();
    await assert.rejects(
      () =>
        parseVoiceAudio('file:///cache/meal.m4a', 'Dinner', '2026-11-12', {
          signal: abortController.signal,
        }),
      (err) => {
        assert.ok(err instanceof VoiceCloudError);
        assert.equal(err.errorCategory, 'upload_canceled');
        return true;
      },
    );

    // Raw JSON / model identifier sanitization (never leaked to ordinary users)
    const clean502 = sanitizeVoiceUserMessage(
      '{"error":"nvidia/nemotron-3-ultra-550b-a55b:free HTTP 502 gemini-3.5-flash"}',
      502,
    );
    assert.ok(!clean502.includes('nemotron'));
    assert.ok(!clean502.includes('gemini-3.5-flash'));
    assert.ok(!clean502.includes('{'));
    assert.ok(!clean502.includes('502'));

    // Quota exhaustion 429 with Retry-After header
    globalThis.fetch = async () => ({
      ok: false,
      status: 429,
      headers: new Headers({
        'Retry-After': '18',
        'X-Error-Category': 'daily_quota_exhausted',
      }),
      json: async () => ({
        detail: 'gemini-3.5-flash quota exhausted',
      }),
    });

    await assert.rejects(
      () => parseVoiceAudio('file:///cache/meal.m4a'),
      (err) => {
        assert.ok(err instanceof VoiceCloudError);
        assert.equal(err.status, 429);
        assert.equal(err.retryAfterSeconds, 18);
        assert.ok(!err.message.includes('gemini-3.5-flash'));
        return true;
      },
    );
  } finally {
    globalThis.fetch = originalFetch;
    if (originalEnv !== undefined) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});
