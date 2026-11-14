import test from 'node:test';
import assert from 'node:assert/strict';
import { recognizeFoodFromImage } from '../src/services/aiFoodRecognition.ts';
for (const base64 of [undefined, 'synthetic']) {
  test(`photo cancellation aborts transport and permits retry (${!!base64})`, async (t) => {
    let calls = 0;
    t.mock.method(globalThis, 'fetch', async (_url, { signal }) => {
      calls++;
      if (calls === 1)
        return new Promise((resolve, reject) =>
          signal.addEventListener('abort', () =>
            reject(new DOMException('private content', 'AbortError')),
          ),
        );
      return Response.json({
        success: true,
        summary: '',
        items: [],
        warnings: [],
      });
    });
    const controller = new AbortController();
    const pending = recognizeFoodFromImage('file:///mock.jpg', base64, {
      signal: controller.signal,
    });
    controller.abort();
    await assert.rejects(pending, /canceled/);
    await assert.rejects(
      () =>
        recognizeFoodFromImage('file:///mock.jpg', base64, {
          signal: controller.signal,
        }),
      /canceled/,
    );
    assert.equal(calls, 1);
    assert.equal(
      (await recognizeFoodFromImage('file:///mock.jpg', base64)).success,
      true,
    );
  });
  test(`photo errors never expose backend details (${!!base64})`, async (t) => {
    t.mock.method(globalThis, 'fetch', async () =>
      Response.json({ detail: 'secret provider traceback' }, { status: 503 }),
    );
    await assert.rejects(
      () => recognizeFoodFromImage('file:///mock.jpg', base64),
      (e) =>
        /temporarily unavailable/.test(e.message) &&
        !/secret|traceback/.test(e.message),
    );
  });
}

test('late photo response is discarded even when transport ignores abort', async (t) => {
  let finish;
  t.mock.method(
    globalThis,
    'fetch',
    () =>
      new Promise((resolve) => {
        finish = resolve;
      }),
  );
  const controller = new AbortController();
  const pending = recognizeFoodFromImage('file:///mock.jpg', 'synthetic', {
    signal: controller.signal,
  });
  controller.abort();
  finish(
    Response.json({ success: true, summary: '', items: [], warnings: [] }),
  );
  await assert.rejects(pending, /canceled/);
});

for (const base64 of [undefined, 'synthetic']) {
  test(`Android transport cancellation text is sanitized without claiming user cancel or timeout (${!!base64})`, async (t) => {
    for (const error of [
      new Error('fetch failed: Fetch request has been canceled'),
      new DOMException('native cancel', 'AbortError'),
    ]) {
      t.mock.method(globalThis, 'fetch', async () => {
        throw error;
      });
      await assert.rejects(
        () => recognizeFoodFromImage('file:///mock.jpg', base64),
        (e) =>
          /Cannot reach photo analysis/.test(e.message) &&
          !/canceled|timed out|native/.test(e.message),
      );
      t.mock.restoreAll();
    }
  });
  test(`client deadline is distinct from network failure (${!!base64})`, async (t) => {
    t.mock.method(
      globalThis,
      'fetch',
      async (_url, { signal }) =>
        new Promise((resolve, reject) =>
          signal.addEventListener('abort', () =>
            reject(new Error('native fetch failure')),
          ),
        ),
    );
    await assert.rejects(
      () =>
        recognizeFoodFromImage('file:///mock.jpg', base64, { timeoutMs: 5 }),
      /timed out/,
    );
  });
}
