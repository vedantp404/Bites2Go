# Security and privacy plan

## Stage 7 local health-data boundary

Weights, height, personal goals and BMI inputs are sensitive personal data. They are kept in a separate local SQLite KV document, with no new network calls, permissions, analytics, accounts or cloud storage. Device/OS backup and access risks from Stage 5 still apply: this is not app-encrypted storage; clearing/uninstalling host/app data can lose records. Do not use real user data in tests or commit databases, exports or health payloads.

Validate numeric limits, finite values, units, document versions, dates and duplicate identities before writing. Corrupt/unknown records remain recoverable, with mutations blocked and no destructive fallback. Atomic single-key writes, serialized operations, stale-snapshot rejection and idempotent identical retries prevent accidental overwrite/duplication in the app's single-writer model. Expo's existing KV implementation uses parameterized SELECT/UPSERT. No raw values appear in error logs.

The SQLite restart test creates synthetic data only in an isolated temporary database and removes it after closing. Physical Android persistence, device-lock/backup policy and a future export/deletion/privacy release review are not established by automated tests. Existing 5 low / 3 high Expo-tooling advisories remain; no forced dependency changes.

## Current Stage 5 local-data boundary

Stage 5 intentionally stores personal diary entries locally in Expo SQLite, without app-added uploads, analytics, accounts, tracking or new runtime permissions. Existing future backend/RLS plans below are not implemented and are not prerequisites for this explicitly authorized local-only scope.

The database is not application-encrypted or protected by an app login. Device lock/access and host/OS backup behavior apply; do not claim that Expo Go storage is an encrypted vault or that OS-level backups are controlled by this app. Uninstalling, clearing host/app data or device loss may remove the diary; there is no implemented export/backup/sync. Use sample records for development. Public release requires a reviewed backup/encryption/retention policy. Never commit native database files or logs containing diary contents; existing Git ignores cover databases and build artifacts. Errors preserve records and expose no raw stored payload.


Stage 1 requirements; policies and controls are not implemented. Treat nutrition diaries, weights, preferences and photos as sensitive personal information.

## Threats and trust boundaries

Principal threats: cross-user record access, forged quantities/snapshots, privileged keys in APKs, upload abuse, AI prompt injection, unintended photo retention, duplicate writes, logging sensitive data and dependency compromise. Validate at every boundary; UI checks alone provide no authorization.

## Secrets and authentication

Only public API base URL, Supabase project URL and publishable key may use `EXPO_PUBLIC_` variables. They are public, including in APKs. Private AI/food keys and migration connection strings stay on backend/operator systems. Prefer runtime secret injection; `.env.example` stays empty. Never ask for secrets in chat or commit local env files. Rotate any leaked secret and review history/exposure instead of merely deleting the current file.

Supabase Auth manages sign-in and refresh. Use a verified secure-storage adapter on Android; never log bearer tokens. Backend validates JWT signature, issuer, audience, expiry and subject with key rotation; reject malformed or expired tokens. Clear private cache and session on logout; refresh failure returns safely to sign-in without discarding an unsaved draft silently. Rate-limit sign-in-sensitive and authenticated endpoints appropriately. Email verification, recovery, redirect/deep-link allowlists and production email delivery are Stage 5 decisions before real users.

## Database authorization

Enable RLS and least-privilege grants on every exposed table. Default deny anonymous access to private rows. SELECT/DELETE require `auth.uid() = user_id`; INSERT uses WITH CHECK; UPDATE needs both USING and WITH CHECK so ownership cannot be reassigned. Child relationships must prove parent ownership as well. Published catalog reads are allowed by policy; user-created foods remain private. Catalog writes require a distinct controlled import role.

Normal FastAPI requests forward the verified user's JWT to the Supabase Data API; never use service role to simulate ownership. Diary writes go through the reviewed atomic function described in Architecture, with direct mutation grants restricted. Check execution grants, function privileges/search path and all indirect access paths. Service/migration roles bypassing RLS must not handle end-user operations. Verify the entire policy with two real user sessions and anonymous access; see [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).

## API validation and operations

Pydantic schemas bound lengths, numeric values, dates, pagination and enum values. Reject nonfinite numbers, oversized quantities and inaccessible referenced versions. Parameterize database operations; never construct SQL from names or search text. Derive owner from token; no arbitrary file paths or remote image fetch URLs from users. Use HTTPS outside local development, explicit CORS policy where relevant, timeouts, bounded responses and per-user/IP rate limits. CORS is not authorization. Public errors contain a safe code/message/request ID, never stack traces, tokens or raw provider responses. Idempotency and optimistic version checks protect retries and concurrent edits.

## Image policy (future Stage 10)

- Explicit consent explains third-party processing and its retention; camera/photo permission is requested only at use. Images are not saved as history by default.
- Provisional application limits: one image per request, maximum 5 MiB encoded file and 20 megapixels decoded. Accept verified JPEG or PNG only; client converts supported HEIC captures or requests another format. Validate magic bytes, decode, dimensions and re-encode stripped of EXIF/location before sending to provider. Enforce byte limits during upload, not only after buffering.
- TLS transfer; process in bounded memory or an access-restricted random temporary file. Delete application temp data in cleanup on success, failure and cancellation; crash leftovers have a sweep target of at most one hour. Verify this operational guarantee before enabling uploads. Do not store images in proxy logs, monitoring attachments or backups.
- Backend deletion does not delete provider audit retention. xAI currently documents default 30-day API input/output retention; a history-disabled request alone must not be advertised as zero retention. Review available ZDR and consent before enabling a provider. Gemini free-tier data use differs from paid; do not send private user photos to a free tier merely to save money. See [Research](RESEARCH.md).
- Model content is untrusted data, including text inside photos. No model has database credentials, arbitrary network tools or diary-write permissions. Bound proposal sizes and validate server-side; no arbitrary suggested URLs are fetched.
- Optional saved photo history requires a separate feature approval: private Supabase Storage bucket, user-owned object paths, storage RLS, short-lived signed URLs, explicit opt-in and user deletion. No public buckets. Account deletion removes objects and references; disclose backup/provider retention separately. Do not implement this storage now.

## User data lifecycle

Minimize collected profile fields. Avoid exact birthdate or health history unless a reviewed feature requires it. No advertising analytics or raw food/photo telemetry in MVP; collect redacted operational errors only. Before public release, provide access/export, account deletion, privacy notice, retention schedule, regional hosting and applicable India/other release-market privacy review. Legal requirements have not been determined in Stage 1; assess them for the chosen audience and jurisdiction before launch.

Keep active private data until user deletion under a published policy. Account deletion must revoke sessions, remove private relational records and opted-in objects, and document backup expiry rather than promise immediate removal from backups. Select and test backups/restore before production; free service tiers are not a backup plan. Recognition metadata retention is provisionally 30 days without payloads; access logs provisionally 14 days redacted, subject to provider/hosting review before deployment.

## Dependencies and Git

Lock dependencies; install only what the current task needs. Review package provenance, supported versions and advisories; test upgrades. Add CI checks once scripts exist, with least-privilege workflow tokens and no secrets in untrusted PR execution. Ignore local envs, keys, builds, databases and uploads. Review staged diff for credentials and sensitive data, including fixtures and screenshots. Synthetic test data only. Never force-push or rewrite shared history without explicit authorization.
