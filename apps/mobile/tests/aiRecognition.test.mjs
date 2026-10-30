import test from 'node:test';
import assert from 'node:assert/strict';
import {
  getBackendBaseUrl,
  checkBackendHealth,
} from '../src/services/aiFoodRecognition.ts';

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
