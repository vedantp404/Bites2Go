# Product completion program

## Authority and baseline — 2026-11-14

The owner's Autonomous Product Completion Program supersedes historical stop-after-stage instructions for the milestones below. Work locally on master, preserve existing edits, and make focused verified commits. **Production master push, Render deploy, EAS builds, APK publication, live inference, production auth, real messages and destructive changes require approval.** No monitoring or background execution is active.

Verified starting commit: `254963f3ff27b4ec5de3ee35c130b52fef0e1ac0`, master, origin `https://github.com/vedantp404/Bites2Go.git`. Existing edits to `.planning/`, mobile package/lock files, voice evaluation CLI and nine catalogue scripts belong to the user and are excluded from this milestone. Installed dependencies include those preexisting edits. No dependency or SQLite schema changes made here.

Baseline: 129 backend / 171 mobile tests pass. No connected adb device. The installed APK/native module version remains unverified. Read-only hosted `/health` and `/openapi.json` returned HTTP 200; OpenAPI advertises audio parsing. This proves neither inference nor the deployed Git revision.

## Executable roadmap

Owner for each milestone: Codex engineering, with owner approval/device acceptance where stated. Status describes local delivery, not production release.

| Milestone | Priority / status | Dependencies | Scope and acceptance | Next action |
| --- | --- | --- | --- | --- |
| R1 Response safety and request tracing | P0 / Validated locally | Existing SDK 58 and AI flows | Reject invalid voice/photo output before review; preserve voice nulls; safe error references; content-free endpoint completion logs; regression suite | Approve/review local commit, then coordinate deploy/build approval separately |
| R2 Voice/photo failure evidence | P0 / Blocked for production evidence | Render access, current APK, explicit live evaluation consent | Correlate real device error to deployment/request; exercise permissions, interruption, retry, body timeouts and duplicate-save guards | Connect Render CLI through browser login and verify installed app build; no personal recording without consent |
| R3 Provider and security hardening | P0 / Planned | R1; R2 traces for routing changes | Audit ingress size bounds, anonymous abuse controls, concurrency, safe client errors; retain bounded fallback/cooldowns; evaluate compatible audit fixes | Start with mocked failure/limit tests; do not benchmark or change production models without approval |
| U1 Premium experience | P1 / In progress (recovery card only) | Existing semantic theme | Use existing cream/green/charcoal/orange language; hierarchy favors daily intake and Add Food; theme all AI states, 48dp controls, large text/TalkBack checks | Voice/photo states first, then dashboard/diary/search; collect light/dark screenshots before declaring visual acceptance |
| A1 Accounts foundation | P1 / Planned | Supabase groundwork; ownership rules below | Mock session lifecycle, explicit local-data adoption, account isolation; no login requirement for offline diary | Implement ownership/consent state tests before mounting an auth SDK |
| N1 Notifications and sync | P2 / Planned | A1 and transactional diary/checkpoint coordinator | Opt-in local reminders/quiet hours first; remote sending and per-owner sync behind approval; no silent account merge | Define local scheduling and cancellation contracts with mocked tests |
| Q1 Release | P1 / Blocked | All P0 issues, security audit, physical device acceptance | CI gates, signed Android continuity, verified deployment revision, consent/privacy, auth isolation and recovery | Prepare CI after R1; keep public release blocked |

For Planned milestones changed files/tests/commit are none. Rollback is no-op until implementation; update this ledger when starting each. Their shared risks are offline-data loss, unmeasured AI accuracy and external-service cost; acceptance must be evidence-based.

## R1 delivered scope and evidence

- `src/services/aiResponse.ts` validates actual JSON before the voice/audio/text and both photo transports return editable results. Missing arrays, invalid fields, nonfinite/negative nutrients, false success and malformed JSON fail clearly. Known-null voice nutrients remain null; empty detection is still a valid result.
- Verified defect: scanner previously replaced invalid/zero photo weight with an invented 100g (`AIFoodScannerModal.tsx`, initial result mapping). Rejecting nonpositive photo weights at the network boundary prevents that branch for AI responses. This is intentionally stricter than the backend's zero-permitting schema. It does not make model estimates accurate or implement unknown-photo-portion review.
- Malformed voice JSON previously fell into `network_error`; now it is `invalid_response`, with no raw response content displayed. Transport cancellation/timeouts remain distinct.
- Application endpoint responses carry server-generated `X-Request-ID`. Routers use the same ID in existing provider timing logs. Incoming IDs are ignored to prevent arbitrary personal content entering logs. Client displays only a 32-hex-character ID; voice error references are selectable.
- `backend/app/request_diagnostics.py` logs a JSON completion event with route template, status/class, latency, outcome, safe error category, backend version and validated `RENDER_GIT_COMMIT` (otherwise unknown). No body, transcript, image, arbitrary URL/query/header or exception text is captured. Existing provider/model/fallback timing logs remain their prior format; this is not a full telemetry platform. CORS preflight is outside this middleware.
- Unexpected backend failures return a generic 500 and a reference ID. Early validation failures also receive IDs. Before any response arrives, network errors naturally have no server reference.
- Profile/config wording distinguishes offline diary storage from optional AI upload to backend/providers. Voice error/retry card now uses semantic theme colors, selectable error references, polite screen-reader announcements and 48dp recovery controls.

Changed files: backend `app/main.py`, `app/request_diagnostics.py`, `app/routers/food.py`, `tests/test_request_diagnostics.py`, `tests/test_timeout_reliability.py`; mobile `src/services/{aiResponse,aiFoodRecognition,voiceFoodLogging}.ts`, `tests/aiResponse.test.mjs`, `src/cloud/config.ts`, `src/screens/ProfileScreen.tsx`, `src/components/VoiceFoodLoggingModal.tsx`; instructions and completion/testing/memory/task documentation.

Tests: baseline 129/171. Final backend 132 pass (existing Starlette/httpx deprecation warning). Existing timing assertions updated to match the returned server-generated reference, retaining timing checks. Mobile full suite 177 pass, including the explicit zero-weight regression. TypeScript, lint, formatting, Expo Doctor 20/20, public config and Android Hermes export pass. No APK build, device test, inference or production change.

Commit: this document belongs to the focused `fix: validate AI results and trace request failures` commit; resolve its exact hash using `git log -1 --format=%H -- docs/PRODUCT_COMPLETION.md`. Push/deploy status: awaiting approval, not released.

Risks: stricter validation can reject incompatible/partial server payloads; manual search stays available and pending voice audio can be retried. Server references appear only once this backend is deployed. Full visual/device validation remains pending. Rollback: revert this focused commit through a new commit; no data migration or destructive restoration is needed. Preserve the user's preexisting work.

## Investigation findings and remaining P0 work

Voice path inspected: native-module availability guard, microphone permission request, Expo recording, duration/size validation, multipart audio upload, 45-second client timeout, 32-second server deadline, in-memory container validation, Gemini parsing, schema/review, explicit diary saveAll. Temporary audio is removed on success/cancel/close; retry retains a failed clip while the modal is open. Existing tests cover synthetic audio, self-corrections and null portions. Neither these tests nor health response establishes real English/Hindi/Hinglish accuracy. The reported phone failure remains unexplained without installed-build and request evidence.

Photo path inspected: camera/gallery picker (base64, quality 0.8), base64 or multipart transport, 45-second timeout, server image validation/resize, Gemini/OpenRouter bounded failover, editable results and explicit diary saveAll. Follow-up: photo external cancellation/unmount, raw HTTP error detail sanitization, consent/provider-retention disclosures and unknown-portion review need a focused pass. Do not infer numeric certainty from valid JSON.

Routing already has bounded primary/fallback budgets and in-process cooldowns; audio is Gemini-specific. No new model chosen without benchmark evidence. Cooldowns do not survive restarts. Backend upload read-before-size-check and unauthenticated abuse controls need explicit investigation before public release. Do not add infrastructure merely to collect traces.

Fresh npm audit: **11 affected package rows: 1 high, 10 moderate**, exit 1. High: Zod oversized-collection memory exhaustion (GHSA-mrhx-c7xc-m3w5). Moderate: minimatch globparts amplification (GHSA-g3hv-75wg-m249), propagated via Expo fingerprint and TypeScript ESLint tooling. Other affected rows: @expo/fingerprint, @typescript-eslint/eslint-plugin, parser, type-utils, typescript-estree, utils, eslint-config-expo, eslint-plugin-expo, expo. Audit suggests some fixes including incompatible major downgrades; none applied. Older 3-high/5-low reports are historical. This run did not change dependencies, so the current snapshot belongs to the preserved existing dependency state, not to this code fix. Public release remains blocked; do not interpret changed counts as remediation.

## Render access and safe diagnostic protocol

No Render CLI, GitHub CLI or RENDER/SUPABASE/FIREBASE environment credentials were found by tool-name/environment-name inspection. Backend AI credentials were not printed. No authenticated Render logs, plan settings or deployment metadata could be inspected. No `.github/workflows` directory exists. Monitoring is **not configured or running**.

Secure setup (operator action; do not paste tokens into chat): install the Windows executable through [official Render CLI instructions](https://render.com/docs/cli), add to PATH, run `render login` and authorize in the browser. Select the intended workspace. Run `render services --output json` to identify Bites2Go, then use a bounded UTC window:

```text
render logs --resources <service-id> --start <UTC-start> --end <UTC-end> --limit 100 --output json
```

Verify supported options with `render logs --help`. Use the displayed application reference plus UTC time and app build to correlate failures. Share only reference ID, operation, app/build, time and error category; omit meal contents, media, tokens and full raw logs. This is manual opt-in sharing, not an implemented automatic report exporter.

[Render CLI reference](https://render.com/docs/cli-reference) supports noninteractive bounded log queries. [Runtime logging](https://render.com/docs/logging) is available; Render HTTP request logs need Pro or higher. A future explicitly configured monitor should group status/category/latency/deployment locally, check health at a modest approved interval and retain aggregates rather than private raw logs. Alerts/GitHub issue creation remain unimplemented. Keep any future CI token in a secret manager; see [API security](https://render.com/docs/api).

## Account and visual direction

Retain Supabase Auth/PostgreSQL rather than introduce Firebase: existing RLS/CAS migrations and owner-bound three-way sync/checkpoints already match the diary model. [Supabase React Native](https://supabase.com/docs/guides/auth/quickstarts/react-native), [Google OAuth](https://supabase.com/docs/guides/auth/social-sign-in/auth-google) and [email OTP](https://supabase.com/docs/guides/auth/auth-email-passwordless) cover the requested methods. [Firebase Auth](https://firebase.google.com/docs/auth) is viable, but a Firestore layer would add another conflict model; [Expo's Firebase guide](https://docs.expo.dev/guides/using-firebase/) distinguishes JS SDK from native development-build integration. Recheck [Supabase pricing](https://supabase.com/pricing), [Firebase pricing](https://firebase.google.com/pricing) and production [SMTP limits](https://supabase.com/docs/guides/auth/auth-smtp) before activation; no paid service selected.

Auth acceptance: continue anonymously offline; login never uploads automatically; explicit owner-bound adoption; account switch never adopts another person's diary; logout cancels in-flight work and keeps local data; expired sessions recover safely. Implement PKCE/deep links, secure session storage, refresh and server JWT verification before enabling cloud. Existing diary/checkpoint writes need a serialized transactional coordinator. Mock these cases first. Configuration alone does not mount accounts or sync.

Keep existing semantic theme rather than replace the app: cream/green/orange light, charcoal/mint dark, system mode, native typography, consistent rounded surfaces and real data. Next visual slice is the remaining AI recording/review/loading states, then dashboard hierarchy and quick actions. Error recovery card is implemented; broad redesign, screenshots, dynamic-text/TalkBack and device acceptance are pending. No visual perfection claim from compilation.
