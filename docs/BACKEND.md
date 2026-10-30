# Stage 9 backend foundation and rollout

## Current delivery and limits

This is the brief's **no-cloud-configuration fallback**, not an operational cloud release. Inspection found no project URL/public key in the repository environment files or process environment. No account, external project, subscription or deployment was created. No credentials were requested or invented. No private local data was read, copied or uploaded. Existing SQLite providers, startup and local write paths remain unchanged.

Implemented: public-config validation and an honest Profile status card; account-bound diary sync planning, upload transport interface and guarded in-memory download merge; optional isolated checkpoint repository; a Supabase/PostgreSQL migration with RLS and revision-checked RPC; tests using mocked transport, real SQLite and isolated PostgreSQL. The checkpoint repository and transport are **not mounted by the app**. Adding environment values alone cannot enable them. Registration/login/logout/session restoration, secure session persistence, real HTTP transport, consent/conflict screens and background sync remain unimplemented until a development backend can be configured and tested. No records currently synchronise, and no realtime behaviour is claimed.

## Provider comparison and decision

Official documentation checked 2026-10-30. Prices/quotas below are verified published figures at review time, not guarantees or forecasts. Taxes, location, email delivery and usage can change costs; recheck before rollout. No paid infrastructure is required for this foundation.

| Consideration | Supabase (selected) | Firebase | Custom/self-hosted |
| --- | --- | --- | --- |
| Free capacity/cost | Free: 500 MB database, 50,000 MAU, 5 GB egress; two active projects; pause after one inactive week. Pro starts at USD 25/month. | Firestore free quota: 1 GiB stored, 50,000 reads/day, 20,000 writes/day, 20,000 deletes/day, 10 GiB outbound/month. Paid use is operation/location dependent. | No hosted free-tier assumption; operator pays for compute, backups and maintenance. |
| Auth | Managed password/verification/recovery and session SDK; email configuration/rate limits need checking. | Managed password and federated auth; phone/other provider billing must be checked separately. | Must operate/secure auth or integrate a managed provider. |
| Data/access | PostgreSQL, SQL constraints, RLS and transactional functions. | Firestore documents, client Security Rules; server/Admin access uses separate IAM. | Full control, full responsibility for authorization/operations. |
| Export/portability | Standard PostgreSQL dump/restore; provider-specific Auth and RPC adapters still need migration work. | Managed export requires billing/Blaze and storage; document/rules model increases migration work. | SQL can be portable; deployments and custom APIs become maintenance obligations. |
| Offline/Expo | Expo/React Native supported. Keep this app's SQLite and implement explicit sync. | JS SDK can work in Expo Go; React Native Firebase requires a native build. Firestore persistence uses last-write-wins for conflicting document changes; do not assume native caching in a JS SDK replaces SQLite. | SQLite still requires a synchronization protocol and transport. |
| Security/maintenance | Provider operates hosted infrastructure; app owns policies, consent, secrets/session handling, migrations and backups. | Provider operates infrastructure; app owns rules, IAM configuration, consent and cost monitoring. | Operator additionally patches infrastructure, certificates, database/auth, monitoring and backups. |

Sources: [Supabase pricing](https://supabase.com/pricing), [password auth](https://supabase.com/docs/guides/auth/passwords), [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [backup/restore](https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore), [Expo integration](https://docs.expo.dev/guides/using-supabase/); [Firestore quota](https://firebase.google.com/docs/firestore/quotas), [billing](https://firebase.google.com/docs/firestore/pricing), [Firebase Auth](https://firebase.google.com/docs/auth), [Security Rules](https://firebase.google.com/docs/firestore/security/get-started), [export](https://firebase.google.com/docs/firestore/manage-data/export-import), [offline semantics](https://firebase.google.com/docs/firestore/manage-data/enable-offline), [Expo Firebase guidance](https://docs.expo.dev/guides/using-firebase/); [Supabase self-hosting](https://supabase.com/docs/guides/self-hosting).

Fit judgment: Supabase's SQL transactions, ownership constraints and export path fit existing historical snapshots. Firebase is viable, but its second offline cache and document conflict model do not remove the need for a SQLite-aware merge protocol. No custom FastAPI service is needed for this first slice. Earlier proposed backend-stack sections are superseded for Stage 9; future privileged operations must remain on trusted infrastructure.

## Data scope and cloud schema

Only diary snapshots are in the first protocol. `public.diary_records` has `(owner_id, record_id)` as its primary key, a positive integer revision, nullable JSONB payload and server `updated_at`. `owner_id` references `auth.users` with deletion cascade. The unchanged version-1 diary payload includes food identity/name, local date/meal, quantity/units, per-100-g reference and calculated nutrients, provenance and original timestamps. Client IDs are preserved, not regenerated on retry. Server revision, not client clock, determines concurrency.

SQL validates record IDs and bounded payload shape/identity (32 KiB maximum); shared mobile `assertEntry` validates full nutrient/date semantics before planning/applying. SQL does **not** currently implement all nutrition validation. Invalid owner-owned payloads can cause a safe client sync failure, not access another account. Stronger server payload validation and payload-version evolution need review before production.

| Existing data | Stage 9 treatment |
| --- | --- |
| Food diary including custom/recipe historical snapshots | Designed first sync slice; no actual uploads in this build. |
| Weight measurements, height, weight goals, effective-dated nutrition targets | Local only; later separate account-owned tables/revisions after the diary slice is accepted. |
| Custom foods, recipe ingredient snapshots, favourites | Local only; historical diary snapshots are independently meaningful. Later sync needs stable references and atomic favourite/source deletion. |
| Appearance | Device-specific; keep local. |
| Built-in food catalogue, calculated totals, BMI, recents | Do not duplicate per account; bundled or derived. |

`supabase/migrations/202610300001_diary_sync.sql` is a new cloud migration only. No existing SQLite table/key is rewritten. Optional `bites2go.sync.diary.v1` checkpoint starts absent and is written only by a future reviewed integration. It contains owner binding, explicit approved IDs and acknowledged row baselines, not credentials. Local histories currently have no account ownership; they must never be automatically assigned merely because somebody signs in.

## Authorization

RLS enabled/forced on the only application cloud table. Authenticated SELECT requires `auth.uid() = owner_id`; anonymous access is denied. Direct insert/update/delete grants and policies are absent. `put_diary` is a narrowly scoped SECURITY DEFINER function with an empty search path, explicit schema references and ownership derived exclusively from `auth.uid()`; it accepts no caller-supplied owner. Only authenticated execution is granted. An account/record advisory transaction lock serializes concurrent creates; row locking and expected revisions protect updates. Public/anonymous RPC access is revoked. No service-role key is used on clients. Migration ownership and function grants must be rechecked in the actual deployment.

## Sync contract and conflict rules

This section defines the tested boundary, not an active worker:

1. Consent must display the verified account, selected diary count/date range and fields leaving the device. `consentToDiary` binds only explicitly selected IDs to that account. A binding cannot be reassigned to a different account by the checkpoint repository. New IDs are not implicitly enrolled. No bulk history upload on login.
2. Load SQLite immediately, without awaiting a cloud request. Read the prior checkpoint and obtain a verified unexpired session through the future SDK adapter. `Session` is a gate input, **not** a JWT validator. Recheck account/expiry after network awaits and before local application; logout/account switching invalidates in-flight work.
3. Fetch all pages of the account's cloud snapshot before planning. The planner rejects duplicate IDs, wrong ownership, malformed nutrition, decreasing revisions, same-revision changed payloads or missing previously acknowledged rows. Omission is not deletion. Full-snapshot pagination needs a concrete transport implementation; large histories require an indexed/cursor protocol before scaling.
4. Compare local, last acknowledged base and remote per ID. Local-only change produces upload with expected revision; remote-only change produces download; identical state produces a checkpoint/no-op; two differing changes produce a conflict. Edit/delete conflicts are conflicts too. Stop that record and retain both versions for explicit future Keep local/Use cloud UI; never silently last-write-wins or recalculate an old diary from the current food catalogue.
5. The RPC atomically inserts/updates one row. Same resulting payload on retry returns the existing revision; stale different payload raises SQLSTATE 40001. A lost acknowledgement is recovered by retry/re-fetch, not by creating another ID. Future transport must map SQL rows to `CloudRow` and preserve conflict/error distinctions; the current boundary's generic failure retains local changes without logging raw provider errors.
6. Local deletion produces a null payload tombstone. Tombstones remain indefinitely in this first protocol so old devices cannot resurrect a deleted row silently. Hard deletion is reserved for verified account/cloud deletion. A later garbage-collection policy requires device acknowledgement rules.
7. `applyDownload` changes only the selected entry after comparing the expected local snapshot again. Unrelated entries stay intact; newer local edits stop the apply. Checkpoint only after a confirmed upload or successful local apply. Pending work is derived from durable local entries versus acknowledged baselines, avoiding a second duplicate outbox. Per-record partial success can checkpoint independently; failed records remain pending.
8. Before wiring into production, combine diary application and checkpoint advancement through a tested transactional/serialized local coordinator. Current helpers do not provide an atomic multi-key commit or a background queue, and are deliberately disconnected. Do not call raw KV writes around existing diary repository queues. Explicit migration to indexed rows may be appropriate at that point.

## Exact setup and remaining rollout work

1. The user selects/creates a **free development** Supabase project (not done by this task), chooses a region and reviews provider terms. Do not enable billing automatically. Retain database credentials only in private tooling, never Expo variables.
2. Review/apply `supabase/migrations/202610300001_diary_sync.sql` once using the development project's SQL editor or migration tooling. Do not run `bootstrap-local.sql` on a real project. Verify RLS/grants/function owner and take backups before later schema changes.
3. Copy `apps/mobile/.env.example` to `apps/mobile/.env.local`; set `EXPO_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co` and the project's `sb_publishable_...` client key. These values are public in the app bundle. No service-role/secret key, JWT, password or database URL belongs here. The validator deliberately supports hosted HTTPS project URLs and publishable keys only. Do not paste secrets into chat. **This does not enable authentication/sync yet.**
4. Configure email/password auth, verification/recovery redirect allowlists and development email delivery/rate limits. Implement registration, sign-in, restore, refresh/expiry and sign-out with the official [React Native SDK guidance](https://supabase.com/docs/guides/auth/quickstarts/react-native). Do not implement password storage or a custom auth protocol.
5. Add only Expo-compatible dependencies when that live slice is ready, including a secure SDK storage adapter backed by [Expo SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/). Test large-session storage failure, restart/refresh, foreground handling and logout. Never fall back to plaintext SQLite/AsyncStorage for tokens. Password fields must remain transient and never logged. Secure storage alone is not a claim of complete security.
6. Implement authenticated paginated transport, bounded/time-limited requests, consent preview, per-record conflict UI and local transactional coordination. Show pending count, last confirmed sync and recoverable errors only from actual state. Keep startup/local writes independent. No realtime listeners in this slice.
7. Run two real development accounts plus anonymous/expired sessions through Auth and PostgREST/RPC: registration/verification/login/logout/restore, account isolation, direct-write denial, lost responses, concurrent devices, pagination, offline startup, revocation and cross-account in-flight responses. Local SQL tests cannot prove gateway JWT verification or hosted configuration.
8. Test Android consent, airplane-mode logging/restart, selected historical dates, deletion/conflict recovery, narrow screens, TalkBack and all themes before enabling any user upload. No physical-device launch was tested in this task.

## Deletion, export and privacy

In this build nothing leaves the device. The proposed diary slice uploads only explicitly selected snapshots and account identity required by the provider. It includes food names, dates, portions and nutrition, so treat it as private. No analytics, photographs or health profile fields are sent.

Future sign-out must stop sync, clear/revoke session material and leave all local records/checkpoints intact. Because the local database is currently a shared device workspace, sign-out is **not** a local privacy lock. Do not let a second account adopt/upload it; require an explicit, separately designed workspace/export/reset flow. This is blocked rather than silently transferring data.

Single diary deletion uses tombstones. Future account deletion requires recent authentication and a trusted server/admin operation that revokes sessions and deletes the Auth user, cascading cloud diary rows. Offer cloud-only deletion separately from local removal; do not clear device records without explicit confirmation. Define backup retention and provider recovery windows before claiming complete erasure. No account deletion UI or privileged endpoint ships here.

Export strategy: a future user-triggered, versioned JSON export from local repositories should cover diary/health/library/appearance without tokens, with a preview and explicit destination/share confirmation. Do not automatically write private data to logs, Git or public storage. Cloud portability uses reviewed PostgreSQL export tooling; an administrative dump is not a user-facing export. Neither export UI nor legal compliance is claimed in this stage.

## Verification commands and scope

From the repository root: `powershell -NoProfile -File scripts/test-cloud-sql.ps1`. Requires local PostgreSQL binaries on PATH. It creates a uniquely named temporary cluster bound only to loopback on a temporary port, uses synthetic Auth schema/roles/identities, applies the actual migration, tests RLS/grants/CAS/tombstones/cascade, stops the process and deletes only that checked temporary directory. No existing database/service is accessed. Local trust authentication is confined to this short-lived synthetic test cluster, never deployment configuration.

From `apps/mobile`: `npm test`, `npm run typecheck`, `npm run lint`, `npm run format:check`, `npx expo-doctor`, `npx expo config --type public`, `npx expo export --platform android --output-dir <temporary-directory>`, `npm audit`.

Boundary tests use a mocked upload transport. SQLite and PostgreSQL persistence/policy tests execute real local database engines. Supabase Auth, email delivery, HTTP/JWT gateway, secure session storage and native Android rendering are not tested or claimed operational. No Stage 10 work.
