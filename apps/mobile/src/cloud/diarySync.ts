import { assertEntry, decodeDiary } from '../domain/diary.ts';
import type { DiaryEntry } from '../domain/diary.ts';
export type CloudRow = {
  ownerId: string;
  id: string;
  revision: number;
  entry: DiaryEntry | null;
};
export type SyncState = {
  version: 1;
  ownerId: string;
  approvedIds: string[];
  base: CloudRow[];
};
// The eventual SDK adapter supplies a verified session; this gate does not verify JWTs.
export type Session = { userId: string; expiresAt: number } | null;
export type SyncAction = {
  kind: 'upload' | 'download' | 'checkpoint' | 'conflict';
  id: string;
  expectedLocal: DiaryEntry | null;
  remote: CloudRow;
  next: DiaryEntry | null;
};
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const recordId = /^[a-zA-Z0-9:-]{1,120}$/;
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object')
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${JSON.stringify(k)}:${canonical(v)}`)
      .join(',')}}`;
  return JSON.stringify(value);
}
function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value));
}
export function same(a: unknown, b: unknown) {
  return canonical(a) === canonical(b);
}
function validateEntries(entries: DiaryEntry[]) {
  entries.forEach(assertEntry);
  decodeDiary(JSON.stringify({ version: 1, entries }));
}
export function assertRow(row: CloudRow, owner: string) {
  if (
    !row ||
    row.ownerId !== owner ||
    typeof row.id !== 'string' ||
    !recordId.test(row.id) ||
    !Number.isSafeInteger(row.revision) ||
    row.revision < 1 ||
    row.revision > 2147483647
  )
    throw Error('Invalid cloud record or account.');
  if (row.entry !== null) {
    assertEntry(row.entry);
    if (row.entry.id !== row.id) throw Error('Cloud identity mismatch.');
  }
}
export function validateSyncState(state: SyncState): SyncState {
  if (
    !state ||
    state.version !== 1 ||
    typeof state.ownerId !== 'string' ||
    !uuid.test(state.ownerId) ||
    !Array.isArray(state.approvedIds) ||
    !Array.isArray(state.base) ||
    state.approvedIds.some(
      (id) => typeof id !== 'string' || !recordId.test(id),
    ) ||
    new Set(state.approvedIds).size !== state.approvedIds.length
  )
    throw Error('Invalid sync checkpoint. Stored data must be retained.');
  const seen = new Set<string>();
  for (const row of state.base) {
    assertRow(row, state.ownerId);
    if (seen.has(row.id) || !state.approvedIds.includes(row.id))
      throw Error('Invalid sync checkpoint identity.');
    seen.add(row.id);
  }
  return state;
}
export function requireSession(
  state: SyncState,
  session: Session,
  now: number,
) {
  validateSyncState(state);
  if (
    !Number.isFinite(now) ||
    !session ||
    !Number.isFinite(session.expiresAt) ||
    session.expiresAt <= now
  )
    throw Error(
      'Sign in again before synchronising. Local records are unchanged.',
    );
  if (session.userId !== state.ownerId)
    throw Error(
      'This local sync workspace belongs to another account. Upload is blocked.',
    );
}
export function consentToDiary(
  ownerId: string,
  selectedIds: string[],
): SyncState {
  if (!selectedIds.length)
    throw Error('Select records and confirm the account before import.');
  return validateSyncState({
    version: 1,
    ownerId,
    approvedIds: [...selectedIds],
    base: [],
  });
}
// Only complete, paginated-to-exhaustion remote snapshots may be supplied here.
export function planDiarySync(
  state: SyncState,
  local: DiaryEntry[],
  remote: CloudRow[],
  session: Session,
  now: number,
): SyncAction[] {
  requireSession(state, session, now);
  validateEntries(local);
  const cloud = new Map<string, CloudRow>();
  for (const row of remote) {
    assertRow(row, state.ownerId);
    if (cloud.has(row.id)) throw Error('Duplicate cloud record.');
    cloud.set(row.id, row);
  }
  const result: SyncAction[] = [];
  for (const id of state.approvedIds) {
    const base = state.base.find((r) => r.id === id);
    const actual = cloud.get(id);
    if (
      base &&
      (!actual ||
        actual.revision < base.revision ||
        (actual.revision === base.revision && !same(actual.entry, base.entry)))
    )
      throw Error(
        'Incomplete or stale cloud response. Retry without changing local data.',
      );
    const row = actual ?? {
      ownerId: state.ownerId,
      id,
      revision: 0,
      entry: null,
    };
    const entry = local.find((e) => e.id === id) ?? null;
    const previous = base?.entry ?? null;
    if (same(entry, row.entry)) {
      if (actual && (!base || base.revision !== actual.revision))
        result.push({
          kind: 'checkpoint',
          id,
          expectedLocal: entry,
          remote: row,
          next: entry,
        });
    } else if (same(entry, previous)) {
      result.push({
        kind: 'download',
        id,
        expectedLocal: entry,
        remote: row,
        next: row.entry,
      });
    } else if (same(row.entry, previous)) {
      result.push({
        kind: 'upload',
        id,
        expectedLocal: entry,
        remote: row,
        next: entry,
      });
    } else {
      result.push({
        kind: 'conflict',
        id,
        expectedLocal: entry,
        remote: row,
        next: entry,
      });
    }
  }
  return clone(result);
}
export function applyDownload(
  state: SyncState,
  local: DiaryEntry[],
  action: SyncAction,
  session: Session,
  now: number,
): DiaryEntry[] {
  requireSession(state, session, now);
  assertRow(action.remote, state.ownerId);
  const acknowledged = state.base.find((row) => row.id === action.id);
  if (acknowledged && action.remote.revision <= acknowledged.revision)
    throw Error('Download plan is stale. Replan before applying.');
  if (!state.approvedIds.includes(action.id))
    throw Error('Download has not been approved.');
  validateEntries(local);
  if (
    action.kind !== 'download' ||
    action.id !== action.remote.id ||
    !same(action.next, action.remote.entry)
  )
    throw Error('Not a download action.');
  const existing = local.find((e) => e.id === action.id) ?? null;
  if (!same(existing, action.expectedLocal))
    throw Error(
      'Local entry changed during sync. Replan; do not overwrite it.',
    );
  if (action.next && action.next.id !== action.id)
    throw Error('Download identity mismatch.');
  const next = [
    ...local.filter((e) => e.id !== action.id),
    ...(action.next ? [clone(action.next)] : []),
  ];
  validateEntries(next);
  return next;
}
export function checkpoint(state: SyncState, row: CloudRow): SyncState {
  validateSyncState(state);
  assertRow(row, state.ownerId);
  const previous = state.base.find((r) => r.id === row.id);
  if (
    !state.approvedIds.includes(row.id) ||
    (previous &&
      (row.revision < previous.revision ||
        (row.revision === previous.revision && !same(row, previous))))
  )
    throw Error('Unapproved or stale sync checkpoint.');
  return clone({
    ...state,
    base: [...state.base.filter((r) => r.id !== row.id), row],
  });
}

export interface DiaryTransport {
  put(
    id: string,
    expectedRevision: number,
    entry: DiaryEntry | null,
  ): Promise<CloudRow>;
}
export async function uploadAction(
  state: SyncState,
  action: SyncAction,
  transport: DiaryTransport,
  getSession: () => Session,
  now: () => number,
): Promise<CloudRow> {
  requireSession(state, getSession(), now());
  if (
    action.kind !== 'upload' ||
    !state.approvedIds.includes(action.id) ||
    action.remote.id !== action.id ||
    action.remote.ownerId !== state.ownerId ||
    !Number.isSafeInteger(action.remote.revision) ||
    action.remote.revision < 0
  )
    throw Error('Unapproved upload.');
  if (action.next) {
    assertEntry(action.next);
    if (action.next.id !== action.id) throw Error('Upload identity mismatch.');
  }
  const acknowledged = state.base.find((row) => row.id === action.id);
  if (acknowledged && action.remote.revision < acknowledged.revision)
    throw Error('Upload plan is stale. Replan before uploading.');
  let result: CloudRow;
  try {
    result = await transport.put(
      action.id,
      action.remote.revision,
      action.next,
    );
  } catch {
    throw Error(
      'Sync was not confirmed. Keep local changes and retry or check conflicts.',
    );
  }
  requireSession(state, getSession(), now());
  assertRow(result, state.ownerId);
  if (
    result.id !== action.id ||
    result.revision <= action.remote.revision ||
    !same(result.entry, action.next)
  )
    throw Error(
      'Unexpected sync acknowledgement. Keep local changes and replan.',
    );
  return clone(result);
}
