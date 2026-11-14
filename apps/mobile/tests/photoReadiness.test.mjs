import test from 'node:test';
import assert from 'node:assert/strict';
import { preparePhotoAnalysis } from '../src/services/aiFoodRecognition.ts';
const result = { success: true, summary: '', items: [], warnings: [] };
for (const base64 of [undefined, 'synthetic']) {
  test(`cold readiness does not consume inference time or send duplicate photos (${!!base64})`, async (t) => {
    let posts = 0;
    t.mock.method(globalThis, 'fetch', async (url, opts) => {
      if (url.endsWith('/health')) {
        await new Promise((r) => setTimeout(r, 25));
        return Response.json({ status: 'ok' });
      }
      posts++;
      assert.equal(opts.method, 'POST');
      return Response.json(result);
    });
    assert.deepEqual(
      await preparePhotoAnalysis('file:///mock.jpg', base64, {
        readinessTimeoutMs: 500,
        timeoutMs: 15,
      }),
      result,
    );
    assert.equal(posts, 1);
  });
}
test('proxy starting response is retried without uploading; only one AI POST follows readiness', async (t) => {
  let checks = 0;
  let posts = 0;
  t.mock.method(globalThis, 'fetch', async (url) => {
    if (url.endsWith('/health'))
      return ++checks === 1
        ? new Response('<html>starting</html>')
        : Response.json({ status: 'ok' });
    posts++;
    return Response.json(result);
  });
  await preparePhotoAnalysis('file:///mock.jpg', 'synthetic');
  assert.equal(checks, 2);
  assert.equal(posts, 1);
});
for (const canceled of [false, true]) {
  test(`readiness ${canceled ? 'cancel' : 'timeout'} never uploads a photo`, async (t) => {
    let calls = 0;
    const controller = new AbortController();
    t.mock.method(globalThis, 'fetch', async (url, { signal }) => {
      calls++;
      assert.ok(url.endsWith('/health'));
      return new Promise((resolve, reject) =>
        signal.addEventListener('abort', () => reject(new Error('transport'))),
      );
    });
    const pending = preparePhotoAnalysis('file:///mock.jpg', 'synthetic', {
      signal: controller.signal,
      readinessTimeoutMs: 10,
    });
    if (canceled) controller.abort();
    await assert.rejects(pending, canceled ? /canceled/ : /too long to start/);
    assert.equal(calls, 1);
  });
}
test('unhealthy or unreachable service is never treated as recognition success', async (t) => {
  t.mock.method(
    globalThis,
    'fetch',
    async () => new Response('', { status: 403 }),
  );
  await assert.rejects(
    () => preparePhotoAnalysis('file:///mock.jpg'),
    /unavailable/,
  );
  t.mock.restoreAll();
  t.mock.method(globalThis, 'fetch', async () => {
    throw new Error('private technical detail');
  });
  await assert.rejects(
    () => preparePhotoAnalysis('file:///mock.jpg'),
    /Check your connection/,
  );
});
