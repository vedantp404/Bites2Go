import test from 'node:test';
import assert from 'node:assert/strict';
import {
  editVoiceNutrient,
  scaleFoodNutrientsNullable,
  parseVoiceAudio,
  parseVoiceMeal,
  VoiceCloudError,
  matchVoiceItemsToCatalogue,
  buildDiaryEntriesFromVoiceCandidates,
} from '../src/services/voiceFoodLogging.ts';
import { waitForAIBackend } from '../src/services/aiFoodRecognition.ts';
const empty = {
  success: true,
  transcript: '',
  summary: '',
  items: [],
  warnings: [],
  clarifying_questions: [],
};
for (const analyze of [
  () => parseVoiceAudio('file:///synthetic.m4a'),
  () => parseVoiceMeal('synthetic test'),
]) {
  test('voice HTTP errors discard even plausible private/provider details', async (t) => {
    t.mock.method(globalThis, 'fetch', async () => ({
      ok: false,
      status: 503,
      json: async () => {
        throw Error('error body must not be read');
      },
    }));
    await assert.rejects(
      analyze,
      (e) =>
        e instanceof VoiceCloudError &&
        e.status === 503 &&
        !/private|provider|read/.test(e.message),
    );
  });
  test('native unsolicited abort stays network error', async (t) => {
    t.mock.method(globalThis, 'fetch', async () => {
      throw new DOMException('private raw detail', 'AbortError');
    });
    await assert.rejects(
      analyze,
      (e) =>
        e.errorCategory === 'network_error' && !e.message.includes('private'),
    );
  });
}
test('cold voice start uses separate readiness budget then exactly one audio POST', async (t) => {
  let posts = 0;
  t.mock.method(globalThis, 'fetch', async (url, init) => {
    if (url.endsWith('/health')) {
      await new Promise((r) => setTimeout(r, 25));
      return Response.json({ status: 'ok' });
    }
    posts++;
    assert.equal(init.method, 'POST');
    return Response.json(empty);
  });
  await waitForAIBackend({ readinessTimeoutMs: 500 });
  assert.deepEqual(
    await parseVoiceAudio('file:///synthetic.m4a', undefined, undefined, {
      timeoutMs: 15,
    }),
    empty,
  );
  assert.equal(posts, 1);
});
test('late audio completion after cancel is rejected without deleting or reading local files', async (t) => {
  let finish;
  const controller = new AbortController();
  t.mock.method(
    globalThis,
    'fetch',
    () =>
      new Promise((r) => {
        finish = r;
      }),
  );
  const pending = parseVoiceAudio(
    'file:///synthetic.m4a',
    undefined,
    undefined,
    { signal: controller.signal },
  );
  controller.abort();
  finish(Response.json(empty));
  await assert.rejects(pending, (e) => e.errorCategory === 'upload_canceled');
});
test('silence is valid structured recovery, false success with food items is rejected', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    Response.json({
      ...empty,
      success: false,
      warnings: ['No speech detected'],
    }),
  );
  assert.equal((await parseVoiceAudio('file:///synthetic.m4a')).success, false);
});
test('unspecified ingredients retain null nutrition and cannot be saved with invented portions', () => {
  const parsed = {
    food_description: 'Butter',
    quantity: 1,
    unit: 'portion',
    state: 'unspecified',
    portion_specified: false,
    estimated_grams: null,
    calories: null,
    protein: null,
    carbohydrates: null,
    fat: null,
    confidence: 0.4,
    confidence_level: 'low',
    alternatives: [],
  };
  const candidates = matchVoiceItemsToCatalogue([parsed], []);
  assert.equal(candidates[0].calories, null);
  assert.equal(candidates[0].estimated_grams, null);
  assert.throws(
    () =>
      buildDiaryEntriesFromVoiceCandidates(
        candidates,
        'Breakfast',
        '2026-11-16',
      ),
    /positive number of grams/,
  );
});

test('manual nutrition edits scale from the measured portion and preserve unknown nutrients', () => {
  const parsed = {
    food_description: 'Custom meal',
    quantity: 1,
    unit: 'portion',
    state: 'unspecified',
    portion_specified: true,
    estimated_grams: 50,
    calories: null,
    protein: null,
    carbohydrates: null,
    fat: null,
    confidence: 0.4,
    confidence_level: 'low',
    alternatives: [],
  };
  let item = matchVoiceItemsToCatalogue([parsed], [])[0];
  assert.equal(item.fiber, null);
  item = editVoiceNutrient(item, 'calories', '120');
  assert.equal(item.calories, 120);
  assert.equal(item.reference.calories, 240);
  assert.equal(scaleFoodNutrientsNullable(item.reference, 100).calories, 240);
  assert.equal(item.protein, null);
  item = editVoiceNutrient(item, 'protein', '0');
  assert.equal(item.protein, 0);
  item = editVoiceNutrient(item, 'calories', '');
  assert.equal(item.calories, null);
  for (const text of ['-1', 'Infinity', '10abc'])
    assert.throws(() => editVoiceNutrient(item, 'fat', text));
  assert.throws(() =>
    editVoiceNutrient({ ...item, estimated_grams: null }, 'fat', '1'),
  );
});
