import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import {
  emptyHealth,
  inputNumber,
  recordWeight,
  removeWeight,
  saveSettings,
  targetsForDate,
  unsetTargets,
  nutrientProgress,
  bmi,
  weightProgress,
  weightPoints,
  dateOrdinal,
} from '../src/domain/health.ts';
import {
  createHealthRepository,
  healthKey,
} from '../src/storage/healthRepository.ts';
const today = '2026-10-30';
const weight = (id = 'a', date = today, kg = 70) => ({
  id,
  date,
  kg,
  unit: 'kg',
});
const record = (d, w, editing = false) => recordWeight(d, w, editing, today);
const targets = { calories: 2100, protein: 100, carbs: 250, fat: 70 };
const settings = (d, date = today, t = targets, h = 175, w = 65) =>
  saveSettings(d, date, t, h, w, today);
function memory() {
  const state = {
    raw: null,
    readError: false,
    writeError: false,
    ackError: false,
  };
  return {
    state,
    storage: {
      getItem: async (key) => {
        assert.equal(key, healthKey);
        if (state.readError) throw Error('read');
        return state.raw;
      },
      setItem: async (key, value) => {
        assert.equal(key, healthKey);
        if (state.writeError) throw Error('write');
        state.raw = value;
        if (state.ackError) throw Error('ack');
      },
    },
  };
}
test('weight validation, local dates, duplicates and stable chronological ordering', () => {
  let d = record(emptyHealth(), weight());
  d = record(d, weight('b', '2026-02-28', 72));
  assert.deepEqual(
    d.weights.map((w) => w.date),
    ['2026-02-28', today],
  );
  assert.equal(d.weights.at(-1).kg, 70);
  for (const kg of [0, -1, 19.99, 500.01, Infinity, NaN])
    assert.throws(() => record(d, weight('c', '2026-01-01', kg)));
  for (const date of ['2026-02-29', '2026-11-01', '1899-01-01', '2026-1-1'])
    assert.throws(() => record(d, weight('c', date)));
  assert.throws(() => record(d, weight('c', today, 71)), /already exists/);
  assert.throws(() => record(d, weight('c', '2026-01-01'), true), /no longer/);
  assert.equal(
    record(emptyHealth(), weight('leap', '2024-02-29', 20)).weights[0].kg,
    20,
  );
  assert.equal(
    record(emptyHealth(), weight('max', today, 500)).weights[0].kg,
    500,
  );
});
test('edit changes only chosen weight; delete and cancellation preserve other data', () => {
  const d = settings(
    record(record(emptyHealth(), weight()), weight('b', '2026-01-01', 80)),
  );
  const before = JSON.stringify(d);
  const next = record(d, weight('a', '2026-10-29', 71), true);
  assert.equal(JSON.stringify(d), before);
  assert.equal(next.weights.find((w) => w.id === 'a').kg, 71);
  assert.deepEqual(next.nutritionGoals, d.nutritionGoals);
  assert.equal(next.heightCm, 175);
  const removed = removeWeight(next, 'a');
  assert.equal(removed.weights.length, 1);
  assert.equal(removed.weights[0].id, 'b');
  assert.deepEqual(removed.weightGoal, d.weightGoal);
});
test('plain numeric input rejects malformed values and distinguishes unset from zero', () => {
  assert.equal(inputNumber('', 0, 100, true), null);
  assert.equal(inputNumber('0', 0, 100, true), 0);
  assert.equal(inputNumber(' 70.5 ', 20, 500), 70.5);
  for (const v of [
    '-1',
    'NaN',
    'Infinity',
    '1e2',
    '0x10',
    '70kg',
    '1,000',
    '',
    '20.1.2',
  ])
    assert.throws(() => inputNumber(v, 20, 500));
});
test('nutrition goal effective dates preserve history, allow clear/zero and reject limits', () => {
  let d = settings(emptyHealth(), '2026-10-01');
  d = settings(d, today, { ...targets, calories: 2300 });
  assert.deepEqual(targetsForDate(d, '2026-09-30'), unsetTargets);
  assert.equal(targetsForDate(d, '2026-10-29').calories, 2100);
  assert.equal(targetsForDate(d, today).calories, 2300);
  d = settings(d, today, { calories: 0, protein: null, carbs: 0, fat: null });
  assert.equal(d.nutritionGoals.length, 2);
  assert.equal(targetsForDate(d, '2026-11-01').calories, 0);
  assert.equal(targetsForDate(d, '2026-10-29').calories, 2100);
  for (const [key, max] of [
    ['calories', 10000],
    ['protein', 500],
    ['carbs', 1500],
    ['fat', 500],
  ])
    for (const value of [-1, max + 1, NaN, 0.000001])
      assert.throws(() => settings(d, today, { ...targets, [key]: value }));
  assert.throws(() => settings(d, '2026-11-01'));
});
test('remaining and macro progress reuse diary rules including excess, unknown and partial', () => {
  assert.deepEqual(nutrientProgress(1000, 2000), {
    remaining: 1000,
    percent: 50,
    fill: 50,
  });
  assert.deepEqual(nutrientProgress(120, 100), {
    remaining: -20,
    percent: 120,
    fill: 100,
  });
  for (const target of [0, null])
    assert.deepEqual(nutrientProgress(10, target), {
      remaining: null,
      percent: null,
      fill: 0,
    });
  for (const value of [null, 40])
    assert.deepEqual(nutrientProgress(value, 100, true), {
      remaining: null,
      percent: null,
      fill: 0,
    });
  assert.equal(nutrientProgress(null, 100).remaining, null);
  assert.equal(nutrientProgress(0, 100).remaining, 100);
});
test('BMI uses kg/metres squared with one-decimal display and invalid/missing protection', () => {
  assert.equal(bmi(200, 80), 20);
  assert.equal(bmi(175, 70).toFixed(1), '22.9');
  for (const [h, w] of [
    [null, 70],
    [175, null],
    [0, 70],
    [251, 70],
    [175, -1],
    [NaN, 70],
    [175, Infinity],
  ])
    assert.equal(bmi(h, w), null);
});
test('gain/loss goals handle reached, overshoot, regress, maintenance and no baseline', () => {
  const g = (start, target) => ({
    targetKg: target,
    setDate: today,
    start: start === null ? null : { kg: start, date: today },
  });
  assert.equal(weightProgress(75, g(80, 70)).percent, 50);
  assert.equal(weightProgress(75, g(70, 80)).percent, 50);
  assert.equal(weightProgress(70, g(80, 70)).percent, 100);
  assert.equal(weightProgress(70, g(80, 70)).difference, 0);
  assert.equal(weightProgress(65, g(80, 70)).percent, 150);
  assert.equal(weightProgress(65, g(80, 70)).fill, 100);
  assert.equal(weightProgress(85, g(80, 70)).percent, -50);
  assert.equal(weightProgress(85, g(80, 70)).fill, 0);
  assert.equal(weightProgress(70, g(70, 70)).percent, null);
  assert.equal(weightProgress(71, g(70, 70)).difference, -1);
  assert.equal(weightProgress(70, g(null, 65)).percent, null);
  assert.equal(weightProgress(null, g(80, 70)).difference, null);
  assert.equal(weightProgress(70, g(80, 0)).difference, null);
});
test('weight goal start is explicit and stable; first subsequent measurement establishes missing start', () => {
  let d = settings(emptyHealth());
  assert.equal(d.weightGoal.start, null);
  d = record(d, weight('old', '2026-01-01', 80));
  assert.equal(d.weightGoal.start, null);
  d = record(d, weight());
  assert.equal(d.weightGoal.start.kg, 70);
  d = record(d, weight('a', today, 72), true);
  assert.equal(d.weightGoal.start.kg, 70);
  d = settings(d, today, targets, 180, 65);
  assert.equal(d.weightGoal.start.kg, 70);
  d = settings(d, today, targets, 180, 75);
  assert.equal(d.weightGoal.start.kg, 72);
  d = settings(d, today, targets, null, null);
  assert.equal(d.weightGoal, null);
  assert.equal(d.heightCm, null);
  for (const w of [0, 501, -1])
    assert.throws(() => settings(d, today, targets, 175, w));
  for (const h of [0, 99, 251, NaN, Infinity])
    assert.throws(() => settings(d, today, targets, h, 70));
});
test('chart represents only actual points, preserves time gaps and handles single/equal measurements', () => {
  assert.deepEqual(weightPoints([]), []);
  assert.equal(weightPoints([weight()])[0].x, 0.5);
  assert.equal(weightPoints([weight()])[0].y, 0.5);
  const points = weightPoints([
    weight('c', '2026-01-11', 72),
    weight('a', '2026-01-01', 70),
    weight('b', '2026-01-02', 70),
  ]);
  assert.equal(points.length, 3);
  assert.equal(points[1].x, 0.1);
  assert.equal(points[0].y, 0);
  assert.equal(points[2].y, 1);
  assert.equal(dateOrdinal('2024-03-01') - dateOrdinal('2024-02-28'), 2);
});
test('repository empty migration is read-only; failed reads/unknown versions never clear bytes', async () => {
  const { storage, state } = memory();
  const repo = createHealthRepository(storage);
  assert.deepEqual(await repo.load(), emptyHealth());
  assert.equal(state.raw, null);
  for (const raw of [
    'bad',
    JSON.stringify({ ...emptyHealth(), version: 2 }),
    JSON.stringify({ ...emptyHealth(), weights: [weight(), weight()] }),
  ]) {
    state.raw = raw;
    await assert.rejects(repo.load());
    await assert.rejects(repo.save(emptyHealth(), emptyHealth()));
    assert.equal(state.raw, raw);
  }
  state.readError = true;
  await assert.rejects(repo.load());
});
test('serialized repository retries uncertain writes without duplicates; stale forms cannot overwrite', async () => {
  const { storage, state } = memory();
  const repo = createHealthRepository(storage);
  const original = await repo.load();
  const next = record(original, weight());
  state.writeError = true;
  await assert.rejects(repo.save(next, original));
  assert.equal(state.raw, null);
  state.writeError = false;
  state.ackError = true;
  await assert.rejects(repo.save(next, original));
  state.ackError = false;
  assert.equal((await repo.save(next, original)).weights.length, 1);
  const other = record(original, weight('b', '2026-01-01', 80));
  await assert.rejects(repo.save(other, original), /changed/);
  const edited = record(next, weight('a', today, 71), true);
  await Promise.all([repo.save(edited, next), repo.save(edited, next)]);
  assert.equal((await repo.load()).weights[0].kg, 71);
  const deleted = removeWeight(edited, 'a');
  state.ackError = true;
  await assert.rejects(repo.save(deleted, edited));
  state.ackError = false;
  assert.equal((await repo.save(deleted, edited)).weights.length, 0);
});
test('SQLite close/reopen retains weights, height and goals without touching diary or appearance keys', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'bites2go-health-test-'));
  const file = join(dir, 'test.db');
  let db;
  const open = () => {
    db = new DatabaseSync(file);
    db.exec(
      'CREATE TABLE IF NOT EXISTS storage (key TEXT PRIMARY KEY NOT NULL, value TEXT)',
    );
    return createHealthRepository({
      getItem: async (key) =>
        db.prepare('SELECT value FROM storage WHERE key = ?').get(key)?.value ??
        null,
      setItem: async (key, value) => {
        db.prepare(
          'INSERT INTO storage (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
        ).run(key, value);
      },
    });
  };
  try {
    let repo = open();
    db.prepare('INSERT INTO storage VALUES (?,?)').run(
      'bites2go.diary.v1',
      'unchanged diary fixture',
    );
    db.prepare('INSERT INTO storage VALUES (?,?)').run(
      'bites2go.appearance.v1',
      'dark',
    );
    const original = await repo.load();
    const next = settings(record(original, weight()));
    await repo.save(next, original);
    db.close();
    db = null;
    repo = open();
    assert.deepEqual(await repo.load(), next);
    assert.equal(
      db
        .prepare('SELECT value FROM storage WHERE key=?')
        .get('bites2go.diary.v1').value,
      'unchanged diary fixture',
    );
    assert.equal(
      db
        .prepare('SELECT value FROM storage WHERE key=?')
        .get('bites2go.appearance.v1').value,
      'dark',
    );
  } finally {
    db?.close();
    rmSync(dir, { recursive: true, force: true });
  }
});
test('measurement dates and chart spacing stay unchanged across local timezones and DST', () => {
  const moduleUrl = new URL('../src/domain/health.ts', import.meta.url).href;
  const script = `import {dateOrdinal,recordWeight,emptyHealth} from '${moduleUrl}'; const d=recordWeight(emptyHealth(),{id:'x',date:'2026-03-08',kg:70,unit:'kg'},false,'2026-03-09'); console.log(JSON.stringify([d.weights[0].date,dateOrdinal('2026-03-09')-dateOrdinal('2026-03-08')]));`;
  for (const TZ of ['Asia/Kolkata', 'America/Los_Angeles'])
    assert.deepEqual(
      JSON.parse(
        execFileSync(
          process.execPath,
          ['--experimental-strip-types', '--input-type=module', '-e', script],
          {
            env: { ...process.env, TZ },
            encoding: 'utf8',
            stdio: ['ignore', 'pipe', 'pipe'],
          },
        ),
      ),
      ['2026-03-08', 1],
    );
});

test('a measurement older than the saved goal baseline has no percentage', () => {
  const goal = {
    targetKg: 65,
    setDate: '2026-10-30',
    start: { kg: 70, date: '2026-10-30' },
  };
  assert.equal(weightProgress(80, goal, '2026-01-01').percent, null);
  assert.equal(weightProgress(80, goal, '2026-01-01').difference, -15);
});
