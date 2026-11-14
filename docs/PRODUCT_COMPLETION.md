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

## R2/U1 photo cancellation — 2026-11-14

Validated locally: Cancel previously ignored taps during analysis; hidden/unmounted scanner requests could complete into stale state. Scanner openings now own separate state, abort on close/unmount/retry, ignore late results and permission/picker callbacks, and clear previous candidates before retry. Both upload methods accept cancellation, retain bounded timeouts and replace raw backend errors with safe status messages and existing request references. Themed error surface, selectable/announced errors and 48dp Cancel control added. No dependencies, routing, diary or nutrition changes.

Tests: 18 targeted and 182 full mobile tests passed; types, lint (after lifecycle correction), formatting and Doctor20/20 passed. Backend unchanged; no live AI, APK build, push or deploy. Native screen interaction remains untested; next priority is Android close/reopen/retry and picker-dismissal acceptance with approved diagnostics. Existing dependency-audit release blocker remains. All 23 preexisting files checksum-preserved. Owner: Codex. Scope: photo lifecycle only; rollback: revert this focused commit. Commit: resolve via git log for this section.

Phase 1A recovery: interrupted scanner work recovered and final lifecycle lint issues resolved. Added image-picker double-tap guard and a regression rejecting late responses even if transport ignores abort. Final types/lint/format and Doctor20/20 passed. Focused local commit only; Phase 1B and later phases not started. Device failure screenshots and supplied Render successes are not correlated; no diagnosis claimed.

## Phase 1B — photo transport diagnosis (2026-11-14)

Owner: Codex. Status: locally validated correction; physical acceptance blocked on device/build/log evidence. Dependency: Phase 1A `0933fa2a6a149353a9245820985c9bfcf1d8566c`. No production changes or inference performed.

### Evidence

- ADB is installed; `adb devices -l` lists no devices. Installed package/versionCode/build ID/source revision remain unknown. Local config is com.bites2go, 1.0.0/code2; that is not installed-app evidence.
- Authenticated **read-only** EAS query via cached CLI succeeded: latest five Android preview records inspected. Latest FINISHED build `6447f478-40b6-4ff0-9b78-ed5cada2fbbf`, version1.0.0/code2, commit `1f8a11cf933cb2db11bdd789e3f43beebe37c50a`, created 2026-11-11T19:54:07.04Z, completed20:45:51.97Z. Prior FINISHED code2 build `7801d2c8-9bb6-4e39-b196-62f03e9461d0` references d446f5c. Neither contains Phase 1A. Build metadata alone does not prove what was installed or whether an uploaded archive had uncommitted differences.
- Phase1A commit timestamp is November14 19:35:38 IST, after the reported14:08 screenshot. The old raw error and EAS history are consistent with older code. Exact screenshot APK provenance is unconfirmed; no later signed-preview install evidence exists here.
- No Render connector, CLI, RENDER environment credential or standard local Render config was found. Authenticated bounded logs and deployed revision could not be obtained. No backend health call is substituted for request correlation.
- Owner-supplied logs:08:38:26UTC start/6.653s/200/3items;08:39:15UTC start/20.684s/Gemini504 then OpenRouter200/5items. These are successful backend operations, not confirmed matches to the14:08IST(~08:38UTC) failure. Request IDs/deployed commit/device build are absent from the supplied summary. Voice (~08:36UTC) is outside this milestone.

### Cancellation audit and confirmed correction

Phase1A gives each opening fresh state; effect cleanup runs on unmount, not every render. Close aborts and invalidates current work; retry supersedes the prior controller and clears old candidates. Picker cancellation returns without upload, permission/picker callbacks are session-guarded, and rapid picker taps are guarded. The scanner suppresses stale results/errors/finally writes by request identity and signal. Explicit confirm still owns diary persistence; these changes never save automatically.

Both base64 and multipart use one client controller with the existing45s timeout; multipart omits a manual Content-Type boundary, JSON declares application/json. Preparation is synchronous and included in the timer lifetime; event-loop blocking can delay timer delivery. No model retry/deadline change is justified. Cancellation cannot guarantee provider work has already stopped; backend success after client disconnect is possible. No Android-native behavior was measured here.

Reproduced defect remaining in Phase1A: plain Error with `fetch failed: Fetch request has been canceled` bypassed TypeError-only sanitization. Also a native AbortError without our signal firing was wrongly called a timeout. Corrected by preserving only known safe HTTP/validation errors, sanitizing all other transport errors, and using actual controller/external signal state to distinguish client timeout from explicit cancellation. Deliberate cancellation remains silent in the scanner through Phase1A's stale-request guard. This repairs error handling; it does not identify why Android originally canceled.

Remaining hypotheses: older installed client, native networking/interruption, connectivity, or old-client timeout. Supplied successful server durations are below45s, but are uncorrelated and cannot rule out cold-start/upload/body-read delays for the screenshot request. Provider failure is not established as the root cause.

### Verification and rollout gate

22 targeted tests and186 full mobile tests pass; types/lint/format pass; Doctor20/20. New regressions cover plain Android-style Error, unsolicited AbortError and actual timer expiry on both uploads. Phase1A tests retain user cancel/retry, pre-aborted requests, malformed output and late-success rejection. Backend unchanged; no backend suite repeated. SQLite/voice/manual search/calculations are covered by the passing existing mobile suite; no physical-device nonregression claim.

Changed code: photo service and two existing test files only. Updated this milestone, TASKS and MEMORY. Focused local commit is identified by `git log -1 --format=%H -- apps/mobile/tests/photoCancellation.test.mjs`; no push/deploy/build. Rollback: revert the focused commit, without data migration. Existing23 user-modified files are checksum-protected. Audit release blocker unchanged; no dependency changes.

Required next actions (approval before execution): prepare a reviewed source archive containing Phase1A and this correction, preserving signing/package identity; allocate a versionCode above the installed/distributed code (latest known preview code2). Build preview APK using `eas build --platform android --profile preview` only after approval. Install over the existing app with matching signature (no uninstall/data clear); record APK hash/EAS ID/commit/versionCode. Coordinate approved deployment of R1 request tracing to correlate errors; no provider/configuration change is indicated by this evidence.

Physical acceptance (pending):
1. Connect/authorize phone; inspect `adb shell dumpsys package com.bites2go` for version and install/update times. Match artifact/EAS metadata; versionCode alone is insufficient because two earlier builds reused code2.
2. With explicit consent for a small nonprivate test image, record app build, backend deployment commit, UTC time, endpoint and safe request ID. Select image and confirm editable review; repeat using camera. Do not log raw image/meal content.
3. Cancel during processing, close/reopen immediately, dismiss picker and rapidly tap retry. Expect no stale result/error or duplicate request saved. Verify retained selected image after a recoverable error and fresh state after close/reopen.
4. Disable connectivity for one attempt: expect friendly network error, image retained and manual search available. Restore it and retry once with explicit consent. Use a mocked delayed response to verify the existing45s timeout separately; do not artificially overload production.
5. Edit quantities, confirm once, verify exactly one intended save with chosen date/category; restart offline and verify existing diary data. Canceling/retrying must write nothing.
6. Correlate the same request's client outcome with server status and duration. Accept only observed behavior; backend200 alone is insufficient. Store content-free evidence and result per step.

Secure Render setup: install Windows CLI from https://render.com/docs/cli, run `render login` and authorize in browser (no tokens in chat); select workspace and identify service via `render services --output json`. Query only:
`render logs --resources <service-id> --start 2026-11-14T08:35:00Z --end 2026-11-14T08:42:00Z --limit 200 --output json`
Use `render logs --help` to verify flags. Relevant log retention may already have expired; do not interpret an empty result as proof no request occurred. Share only IDs/status/timing/deployment, not raw logs. Official command reference: https://render.com/docs/cli-reference.

Phase1B code is ready for physical acceptance; reliability on the phone is not yet demonstrated. Phase1C voice diagnosis may be authorized separately, but has not started and Phase1 overall remains unaccepted. No Phase2/3 work.

## Device-acceptance release preparation

Prepared1.0.0/code3, same com.bites2go/EAS project, remote signing source and explicit preview backend URL. 186 tests/types/lint/format/Doctor20/20/config/local Android export pass; export credential-pattern scan zero. No cloud build/push/deploy. Preserved23 user edits. Build source must explicitly review the uncommitted package/lock pair; signing/installed-version continuity and final APK secrets scan remain gates. See docs/DEVICE_ACCEPTANCE_RELEASE.md for exact upgrade and acceptance instructions.

## Final preview blockers

Reviewed and included the existing Expo58-compatible package/lock pair unchanged; isolated clean offline npm ci succeeds(800packages), Expo dependency check and npm ls pass. Public EAS default signing metadata obtained; device APK certificate comparison remains pending. Render now200 twice, self-reported1f8a11cf and no X-Request-ID: R1 tracing deployment still needed for correlation. Existing23 file contents preserved;21 unrelated edits remain uncommitted. Exact approval-gated push/clean-checkout/build/install sequence and certificate fingerprint recorded in docs/DEVICE_ACCEPTANCE_RELEASE.md. No push/deploy/build or credential change.

## Phase 1 first-attempt photo recognition — local validation

Owner: Codex. Status: partially validated (automated); device evidence pending. Dependency: release510d61f/versionCode3. No production configuration changes, live inference, push, deployment or cloud build.

Evidence: owner reports20:24IST client timeout; backend startup14:54:14–14:54:26UTC and successful photo starts14:54:55,14:56:12,14:57:50 (21.57s,19.44s,21.49s). Gemini timed out around14–15s each, OpenRouter succeeded. These prove repeated primary latency and working fallback in that excerpt, not correlation with the failed screenshot. Render officially documents free-service spin-down after15min and about1min wake-up: https://render.com/docs/free. Source confirms a single45s client POST budget previously covered wake-up/upload/inference/body; backend default35s starts after arrival. Startup plus successful inference can exceed45s. This design mismatch is confirmed; its occurrence for the screenshot remains a hypothesis.

Implemented: scanner now prepares the service via /health before sending the image, visibly showing Connecting vs Analyzing. Readiness is bounded75s, including GET/body/waits, separately from the unchanged45s recognition budget (backend default35s leaves10s transport margin). Maximum intended active wait120s, with immediate cancellation of both stages. Only /health is retried on starting HTML/502/503/504; no automatic inference POST retries or extra model calls. Airplane-mode/network errors remain failures, readiness status alone is never recognition success. A health success confirms process readiness only, not quota/model availability. Current production deadline overrides still need verification at deployment; transport/body/upload must fit the45s margin. Post-readiness instance restarts can still fail; no zero-failure guarantee.

Photo provider strategy: preserve configured models/order, reserve fallback time, keep existing quota cooldowns. After two observed primary timeouts, bypass that provider/model for120s when a configured fallback exists. This spans the supplied roughly77s/98s scan intervals. Next scan after expiry probes the configured primary; success resets its failure history. State is thread-safe and process-local, resets on restart and is not shared across workers. Cancellation/quota/unconfigured cases keep existing behavior; cooldown is not a claim that OpenRouter is always healthy. No speculative permanent model switch or parallel paid request. A cold process still has no provider history and may spend14s on its primary before fallback.

Changed: photo client service, scanner loading state, backend AI orchestrator, photoReadiness.test.mjs and test_photo_timeout_circuit.py. Tests:15 targeted mobile readiness/cancellation tests;67 targeted backend timeout tests;192 full mobile and133 full backend pass. Types/lint/format, Doctor20/20 and local Android export pass. Mock coverage includes startup longer than inference timeout, proxy loading response, one POST, readiness timeout/cancel/outage, existing analysis timeout/cancel/late-result guards, primary timeout/fallback success and two-timeout bypass across observed intervals with expiry/recovery. Existing voice/diary/calculation suites pass; no schemas/dependencies changed. Known warnings and dependency-audit release blocker remain. Protected21 unrelated file contents remain unchanged.

Commit: resolve this milestone with git log -1 --format=%H -- backend/tests/test_photo_timeout_circuit.py. Rollback: revert focused commit, no migrations. Local source only: deployed backend and versionCode3 APK do not include these changes. Separate approvals required for push/Render deployment and a new preview build (allocate versionCode above3 before building); never reuse the old APK as evidence of this fix.

Device acceptance gate: after an approved deployment/build, record build ID/source/package/versionCode and backend revision/request ID. Leave service idle at least15min with no health polling/other traffic; perform ONE scan using a consented nonprivate image. Repeat at least3 independent idle-to-first-scan cycles, alternating gallery/camera. Pass only if each first scan progresses Connecting→Analyzing→editable results without manual resubmission, within75s readiness +45s analysis, with exactly one recognition POST per attempt. Correlate UTC/client/backend timings and IDs; verify actual production deadline/config. Within a warm session exercise primary-timeout fallback then bypass/recovery using mocks or separately approved minimal evaluation; do not deliberately exhaust production quotas. Cancel during connecting and analyzing, close/reopen, test network-off then restore/retry: no stale result, no writes until explicit save, selected image retained after errors. Confirm editable quantity/nutrition, single confirmed diary entry, existing data and offline restart. Report any failure rather than averaging it away. No device acceptance or accuracy claim from mocked tests. Voice/premium UI/auth not started.
