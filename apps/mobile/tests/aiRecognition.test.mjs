import test from 'node:test';
import assert from 'node:assert/strict';
import {
  getBackendBaseUrl,
  checkBackendHealth,
  recognizeFoodFromImage,
} from '../src/services/aiFoodRecognition.ts';
import { parseVoiceMeal } from '../src/services/voiceFoodLogging.ts';

test('getBackendBaseUrl: resolves default and custom URL values', () => {
  const originalEnv = process.env.EXPO_PUBLIC_AI_BACKEND_URL;
  try {
    delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    const defaultUrl = getBackendBaseUrl();
    assert.ok(defaultUrl.startsWith('http://'));

    process.env.EXPO_PUBLIC_AI_BACKEND_URL = 'http://192.168.1.50:8000/';
    assert.equal(getBackendBaseUrl(), 'http://192.168.1.50:8000');
  } finally {
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
            err.message.includes('temporarily overloaded or unavailable'),
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
  } finally {
    globalThis.fetch = originalFetch;
    if (originalEnv) {
      process.env.EXPO_PUBLIC_AI_BACKEND_URL = originalEnv;
    } else {
      delete process.env.EXPO_PUBLIC_AI_BACKEND_URL;
    }
  }
});
