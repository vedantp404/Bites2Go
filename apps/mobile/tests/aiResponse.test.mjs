import test from 'node:test';
import assert from 'node:assert/strict';
import {
  parseVoiceAudio,
  parseVoiceMeal,
  VoiceCloudError,
} from '../src/services/voiceFoodLogging.ts';
import { recognizeFoodFromImage } from '../src/services/aiFoodRecognition.ts';
import {
  validVoiceResponse,
  validPhotoResponse,
  responseRequestId,
} from '../src/services/aiResponse.ts';

const id = '0123456789abcdef0123456789abcdef';
const voice = {
  success: true,
  transcript: 'an unspecified portion',
  summary: '',
  warnings: [],
  clarifying_questions: [],
  items: [
    {
      food_description: 'Butter',
      quantity: 1,
      unit: 'portion',
      state: 'unspecified',
      estimated_grams: null,
      calories: null,
      protein: null,
      carbohydrates: null,
      fat: null,
      confidence: 0.5,
      confidence_level: 'low',
      alternatives: [],
      portion_specified: false,
    },
  ],
};
const photo = {
  success: true,
  summary: '',
  warnings: [],
  items: [
    {
      food_name: 'Toast',
      estimated_quantity: 1,
      unit: 'slice',
      estimated_grams: 30,
      calories: 80,
      protein: 2,
      carbohydrates: 15,
      fat: 1,
      uncertainty: {
        confidence_score: 0.8,
        confidence_level: 'high',
        alternatives: [],
      },
    },
  ],
};

test('contract guards preserve unknown voice nutrients and reject invalid review data', () => {
  assert.equal(validVoiceResponse(voice), true);
  assert.equal(voice.items[0].calories, null);
  assert.equal(validPhotoResponse(photo), true);
  for (const payload of [
    null,
    {},
    { ...voice, success: false },
    { ...voice, warnings: {} },
    { ...voice, items: [null] },
  ]) {
    assert.equal(validVoiceResponse(payload), false);
  }
  for (const calories of [undefined, '80', -1, NaN, Infinity]) {
    assert.equal(
      validVoiceResponse({
        ...voice,
        items: [{ ...voice.items[0], calories }],
      }),
      false,
    );
    assert.equal(
      validPhotoResponse({
        ...photo,
        items: [{ ...photo.items[0], calories }],
      }),
      false,
    );
  }
});

test('audio, text and both photo transports reject malformed success instead of passing it to review', async (t) => {
  const clients = [
    () => parseVoiceAudio('file:///mock.m4a'),
    () => parseVoiceMeal('synthetic test'),
    () => recognizeFoodFromImage('file:///mock.jpg', 'mock'),
    () => recognizeFoodFromImage('file:///mock.jpg'),
  ];
  for (const body of [
    '<html>proxy error</html>',
    JSON.stringify({ success: true, items: [null] }),
  ]) {
    t.mock.method(
      globalThis,
      'fetch',
      async () => new Response(body, { headers: { 'X-Request-ID': id } }),
    );
    for (const call of clients) {
      await assert.rejects(call, (error) => {
        assert.match(error.message, /invalid result/);
        assert.match(error.message, new RegExp(id));
        assert.equal(error.requestId, id);
        if (error instanceof VoiceCloudError)
          assert.equal(error.errorCategory, 'invalid_response');
        return true;
      });
    }
    t.mock.restoreAll();
  }
});

test('valid audio result retains nulls and empty detection remains a valid result', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json(voice));
  assert.deepEqual(await parseVoiceAudio('file:///mock.m4a'), voice);
  assert.equal(validVoiceResponse({ ...voice, items: [] }), true);
  assert.equal(validPhotoResponse({ ...photo, items: [] }), true);
});

test('only safe opaque server IDs appear in errors; HTTP failures retain a useful reference', async (t) => {
  assert.equal(
    responseRequestId(
      new Response('', {
        headers: { 'X-Request-ID': 'private arbitrary content' },
      }),
    ),
    undefined,
  );
  t.mock.method(globalThis, 'fetch', async () =>
    Response.json(
      { detail: 'Try again later.' },
      { status: 503, headers: { 'X-Request-ID': id } },
    ),
  );
  await assert.rejects(
    () => parseVoiceAudio('file:///mock.m4a'),
    (error) => error.status === 503 && error.requestId === id,
  );
  await assert.rejects(
    () => recognizeFoodFromImage('file:///mock.jpg', 'mock'),
    new RegExp(id),
  );
});

test('body cancellation and network failure stay distinct from malformed output', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => ({
    ok: true,
    json: async () => {
      throw new DOMException('aborted', 'AbortError');
    },
  }));
  await assert.rejects(
    () => parseVoiceAudio('file:///mock.m4a'),
    (error) => error.errorCategory === 'timeout',
  );
  t.mock.restoreAll();
  t.mock.method(globalThis, 'fetch', async () => {
    throw new TypeError('network unavailable');
  });
  await assert.rejects(
    () => parseVoiceAudio('file:///mock.m4a'),
    (error) => error.errorCategory === 'network_error',
  );
});

// Do not let the scanner silently substitute 100g for an invalid AI portion.
test('photo results without a positive measured estimate never reach review', async (t) => {
  for (const estimated_grams of [0, null, -1]) {
    const payload = {
      ...photo,
      items: [{ ...photo.items[0], estimated_grams }],
    };
    t.mock.method(globalThis, 'fetch', async () => Response.json(payload));
    await assert.rejects(
      () => recognizeFoodFromImage('file:///mock.jpg', 'mock'),
      /invalid result/,
    );
    t.mock.restoreAll();
  }
});
