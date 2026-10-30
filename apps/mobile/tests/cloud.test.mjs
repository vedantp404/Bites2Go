import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, sep } from 'node:path';
import { cloudConfiguration } from '../src/cloud/config.ts';
import {
  consentToDiary,
  planDiarySync,
  checkpoint,
  applyDownload as guardedDownload,
  requireSession,
  uploadAction,
  same,
} from '../src/cloud/diarySync.ts';
import {
  createCheckpointRepository,
  syncKey,
} from '../src/cloud/checkpointRepository.ts';
import {
  createDiaryRepository,
  diaryKey,
} from '../src/storage/diaryRepository.ts';
import { createEntry, editPortion } from '../src/domain/diary.ts';
import { foods } from '../src/data/foods.ts';
const owner = '11111111-1111-1111-1111-111111111111';
const other = '22222222-2222-2222-2222-222222222222';
const now = 1000;
const session = { userId: owner, expiresAt: 2000 };
const entry = (id = 'a') =>
  createEntry(
    foods[0],
    'Lunch',
    '2026-10-29',
    100,
    id,
    '2026-10-30T12:00:00.000Z',
  );
const row = (e = entry(), revision = 1) => ({
  ownerId: owner,
  id: e?.id ?? 'a',
  revision,
  entry: e,
});
const bound = () => consentToDiary(owner, ['a']);
const synced = () => checkpoint(bound(), row());
const plan = (state, local, remote) =>
  planDiarySync(state, local, remote, session, now);
const applyDownload = (local, action) =>
  guardedDownload(bound(), local, action, session, now);
const edit = () => editPortion(entry(), 200, '2026-10-30T13:00:00.000Z');
function memory() {
  const values = new Map();
  let fail = false;
  return {
    values,
    fail(value) {
      fail = value;
    },
    storage: {
      getItem: async (k) => values.get(k) ?? null,
      setItem: async (k, v) => {
        if (fail) throw Error('write');
        values.set(k, v);
      },
    },
  };
}
test('configuration is fail-closed and never enables network/auth', () => {
  assert.equal(cloudConfiguration().state, 'missing');
  assert.equal(
    cloudConfiguration('https://example.supabase.co', 'sb_publishable_fixture')
      .state,
    'configured',
  );
  for (const [url, key] of [
    ['http://example.supabase.co', 'sb_publishable_x'],
    ['https://evil.example', 'sb_publishable_x'],
    ['https://user:password@example.supabase.co', 'sb_publishable_x'],
    ['https://example.supabase.co/path', 'sb_publishable_x'],
    ['https://example.supabase.co', 'sb_secret_fixture'],
    ['https://example.supabase.co', 'jwt-legacy'],
    ['', 'x'],
  ])
    assert.equal(cloudConfiguration(url, key).state, 'invalid');
  assert.match(
    cloudConfiguration('https://example.supabase.co', 'sb_publishable_x')
      .message,
    /not enabled/,
  );
});
test('session gating rejects signed-out, expired, malformed and switched accounts without changing local data', () => {
  const state = synced(),
    original = JSON.stringify(state);
  for (const s of [
    null,
    { userId: owner, expiresAt: 1000 },
    { userId: owner, expiresAt: NaN },
    { userId: other, expiresAt: 2000 },
  ])
    assert.throws(() => requireSession(state, s, now));
  requireSession(state, session, now);
  assert.equal(JSON.stringify(state), original);
  assert.throws(() => consentToDiary(owner, []));
  assert.throws(() => consentToDiary('invalid', ['a']));
  assert.throws(() => consentToDiary(owner, ['a', 'a']));
});
test('only explicitly consented IDs upload; no entire-history import or duplicate plan', () => {
  const local = [entry(), entry('private')];
  const original = JSON.stringify(local);
  const actions = plan(bound(), local, []);
  assert.equal(actions.length, 1);
  assert.equal(actions[0].kind, 'upload');
  assert.equal(actions[0].remote.revision, 0);
  assert.deepEqual(plan(checkpoint(bound(), row()), local, [row()]), []);
  assert.equal(JSON.stringify(local), original);
});
test('three-way merge handles local update/delete and remote update/delete', () => {
  const changed = edit(),
    state = synced();
  assert.equal(plan(state, [changed], [row()])[0].kind, 'upload');
  assert.equal(plan(state, [], [row()])[0].next, null);
  const download = plan(state, [entry()], [row(changed, 2)])[0];
  assert.equal(download.kind, 'download');
  assert.deepEqual(applyDownload([entry(), entry('keep')], download), [
    entry('keep'),
    changed,
  ]);
  const deletion = plan(state, [entry()], [row(null, 2)])[0];
  assert.equal(deletion.kind, 'download');
  assert.deepEqual(applyDownload([entry()], deletion), []);
});
test('concurrent edit/edit and edit/delete conflicts preserve both sides', () => {
  const remote = editPortion(entry(), 300, '2026-10-30T14:00:00.000Z');
  for (const [local, cloud] of [
    [[edit()], [row(remote, 2)]],
    [[edit()], [row(null, 2)]],
    [[], [row(remote, 2)]],
  ]) {
    const bytes = JSON.stringify([local, cloud]);
    const action = plan(synced(), local, cloud)[0];
    assert.equal(action.kind, 'conflict');
    assert.throws(() => applyDownload(local, action));
    assert.equal(JSON.stringify([local, cloud]), bytes);
  }
});
test('equal edits or lost acknowledgement checkpoint without duplicate upload', () => {
  const action = plan(synced(), [edit()], [row(edit(), 2)])[0];
  assert.equal(action.kind, 'checkpoint');
  assert.deepEqual(
    plan(checkpoint(synced(), row(edit(), 2)), [edit()], [row(edit(), 2)]),
    [],
  );
  const reordered = Object.fromEntries(Object.entries(entry()).reverse());
  assert.ok(same(entry(), reordered));
});
test('stale, incomplete, wrong-account, malformed and duplicate cloud responses cannot apply', () => {
  for (const remote of [
    [],
    [row(entry(), 1), row(entry(), 1)],
    [{ ...row(), ownerId: other }],
    [{ ...row(), id: 'wrong' }],
    [
      {
        ...row(),
        entry: {
          ...entry(),
          nutrients: { ...entry().nutrients, calories: 999 },
        },
      },
    ],
    [row(edit(), 1)],
  ])
    assert.throws(() => plan(synced(), [entry()], remote));
  assert.throws(() =>
    plan(checkpoint(synced(), row(edit(), 2)), [edit()], [row()]),
  );
  const action = plan(synced(), [entry()], [row(edit(), 2)])[0];
  assert.throws(
    () =>
      applyDownload(
        [editPortion(entry(), 400, '2026-10-30T15:00:00.000Z')],
        action,
      ),
    /changed/,
  );
});
test('diary snapshots retain null nutrients, dates and references through download', () => {
  const e = entry();
  e.reference.fiber = null;
  e.nutrients.fiber = null;
  const action = plan(bound(), [], [row(e)])[0];
  const result = applyDownload([], action);
  assert.deepEqual(result, [e]);
  assert.notEqual(result[0], e);
});
test('mock transport network failure, retry, partial success and expiry keep checkpoints explicit', async () => {
  const local = [entry(), entry('b')];
  const state = consentToDiary(owner, ['a', 'b']);
  const actions = plan(state, local, []);
  const server = new Map();
  let loseAck = true;
  const transport = {
    put: async (id, revision, e) => {
      const existing = server.get(id);
      if (
        existing &&
        !same(existing.entry, e) &&
        existing.revision !== revision
      )
        throw Error('conflict');
      const r = existing ?? { ownerId: owner, id, revision: 1, entry: e };
      server.set(id, r);
      if (loseAck) {
        loseAck = false;
        throw Error('network');
      }
      return r;
    },
  };
  await assert.rejects(
    uploadAction(
      state,
      actions[0],
      transport,
      () => session,
      () => now,
    ),
    /not confirmed/,
  );
  const ack = await uploadAction(
    state,
    actions[0],
    transport,
    () => session,
    () => now,
  );
  assert.equal(server.size, 1);
  const partial = checkpoint(state, ack);
  assert.equal(plan(partial, local, [ack]).length, 1);
  let current = session;
  await assert.rejects(
    uploadAction(
      state,
      actions[1],
      {
        put: async (id, rev, e) => {
          current = null;
          return { ownerId: owner, id, revision: 1, entry: e };
        },
      },
      () => current,
      () => now,
    ),
    /Sign in/,
  );
  assert.equal(state.base.length, 0);
  assert.equal(local.length, 2);
  await assert.rejects(
    uploadAction(
      state,
      actions[0],
      { put: async () => ({ ...ack, ownerId: other }) },
      () => session,
      () => now,
    ),
  );
});
test('checkpoint storage rejects account rebinding, stale changes and corrupt data; retries are idempotent', async () => {
  const mem = memory(),
    repo = createCheckpointRepository(mem.storage);
  assert.equal(await repo.load(), null);
  assert.equal(mem.values.size, 0);
  mem.fail(true);
  await assert.rejects(repo.save(bound(), null));
  mem.fail(false);
  await repo.save(bound(), null);
  await repo.save(bound(), null);
  await assert.rejects(
    repo.save(consentToDiary(other, ['a']), bound()),
    /reassigned/,
  );
  await repo.save(synced(), bound());
  await assert.rejects(
    repo.save(checkpoint(synced(), row(edit(), 2)), bound()),
    /changed/,
  );
  for (const raw of ['bad', '{"version":2}']) {
    mem.values.set(syncKey, raw);
    await assert.rejects(repo.load());
    await assert.rejects(repo.save(bound(), null));
    assert.equal(mem.values.get(syncKey), raw);
  }
});
test('SQLite reopen preserves sync checkpoint and all existing offline keys', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'bites2go-sync-test-'));
  let db;
  const open = () => {
    db = new DatabaseSync(join(directory, 'test.db'));
    db.exec(
      'CREATE TABLE IF NOT EXISTS storage (key TEXT PRIMARY KEY NOT NULL,value TEXT)',
    );
    return {
      getItem: async (key) =>
        db.prepare('SELECT value FROM storage WHERE key=?').get(key)?.value ??
        null,
      setItem: async (key, value) => {
        db.prepare(
          'INSERT INTO storage VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
        ).run(key, value);
      },
    };
  };
  try {
    let storage = open();
    const diary = createDiaryRepository(storage);
    await diary.save(entry());
    for (const key of [
      'bites2go.health.v1',
      'bites2go.library.v1',
      'bites2go.appearance.v1',
    ])
      await storage.setItem(key, 'offline-fixture');
    const before = await storage.getItem(diaryKey);
    await createCheckpointRepository(storage).save(synced(), null);
    db.close();
    db = null;
    storage = open();
    assert.deepEqual(
      await createCheckpointRepository(storage).load(),
      synced(),
    );
    assert.equal(await storage.getItem(diaryKey), before);
    for (const key of [
      'bites2go.health.v1',
      'bites2go.library.v1',
      'bites2go.appearance.v1',
    ])
      assert.equal(await storage.getItem(key), 'offline-fixture');
  } finally {
    db?.close();
    assert.ok(resolve(directory).startsWith(resolve(tmpdir()) + sep));
    assert.ok(directory.includes('bites2go-sync-test-'));
    rmSync(directory, { recursive: true, force: true });
  }
});

test('logout or account switch during download blocks local application', () => {
  const action = plan(synced(), [entry()], [row(edit(), 2)])[0];
  for (const changedSession of [null, { userId: other, expiresAt: 2000 }]) {
    assert.throws(() =>
      guardedDownload(synced(), [entry()], action, changedSession, now),
    );
  }
  assert.throws(() =>
    guardedDownload(
      consentToDiary(owner, ['other-id']),
      [entry()],
      action,
      session,
      now,
    ),
  );
});

test('a newer checkpoint invalidates an older in-flight download or upload plan', async () => {
  const oldDownload = plan(synced(), [entry()], [row(edit(), 2)])[0];
  const newer = checkpoint(synced(), row(entry(), 3));
  assert.throws(
    () => guardedDownload(newer, [entry()], oldDownload, session, now),
    /stale/,
  );
  const oldUpload = plan(synced(), [edit()], [row()])[0];
  let called = false;
  await assert.rejects(
    uploadAction(
      newer,
      oldUpload,
      {
        put: async () => {
          called = true;
          return row(edit(), 4);
        },
      },
      () => session,
      () => now,
    ),
    /stale/,
  );
  assert.equal(called, false);
});
