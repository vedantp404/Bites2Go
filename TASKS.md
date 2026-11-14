## Current completion program — R1, 2026-11-14

- [x] Inspect actual master/dependencies/AI paths, preserve existing edits, establish 129 backend / 171 mobile baseline.
- [x] Implement and test AI response validation, safe request tracing and invalid-photo-weight rejection.
- [x] Correct upload disclosure and apply semantic theme/48dp recovery controls.
- [x] Verify 132 backend and 177 mobile tests, types/lint/format, Doctor20/20, config and Android export.
- [x] Record fresh failing audit (1 high / 10 moderate), roadmap, rollback, Render access limits and account recommendation in docs/PRODUCT_COMPLETION.md.
- [ ] Verify physical device behavior and identify the reported production voice failure with correlated logs.
- [ ] Obtain production push/deploy/build approval; no remote release performed in this run.
- [ ] Complete remaining reliability/UI/account/notification/release milestones in the dependency-aware roadmap.

# Ordered roadmap

## Milestone 4F — Rebuild Voice Logging Around Audio-Native AI — implemented (awaiting push, deploy & preview APK rebuild approval)

- [x] Diagnosed why OS STT (`expo-speech-recognition`) + text LLM + offline catalogue matcher dropped dish specificity and corrupted food/self-correction cues (`"two scrambled eggs"` -> `"okay to scramble eggs"`, `"sourdough toast"` -> `"Sodu toast"`, `"actually make that two"` -> `"Chili make it that to"`, `"whey protein"` -> `"a protein"`), compounded by OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` JSON truncation at low output tokens.
- [x] Evaluated Gemini audio capabilities via live API metadata & single synthetic silent WAV probe (`$0` / minimal free call, no batch benchmarks): `gemini-3.5-flash` accepts all target audio MIMEs (`audio/mp4`, `audio/m4a`, `audio/aac`, `audio/mpeg`, `audio/wav`, `audio/ogg`, `audio/webm`) and returned valid empty-food JSON in `3.859s` with `ThinkingConfig(thinking_budget=0)` and `VoiceMealParseResponse`; `gemini-2.5-flash` returned `404 NOT_FOUND`. OpenRouter `:free` catalog offered only `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` (`$0`), avoided to prevent reasoning truncation chains.
- [x] Built backend audio-native endpoint `POST /api/v1/parse-voice-audio` (`backend/app/routers/food.py`, `backend/app/services/audio.py`, `backend/app/services/providers/gemini_provider.py`, `backend/app/services/ai_service.py`, `backend/app/models/food.py`, `backend/app/config.py`, `backend/app/routers/health.py`): in-memory byte/MIME/magic validation (`32 B` min, `10 MB` max), `gemini-3.5-flash` primary (`VOICE_AUDIO_TIMEOUT_SECONDS=18.0`, `VOICE_AUDIO_SERVER_DEADLINE_SECONDS=32.0`, `VOICE_AUDIO_MAX_OUTPUT_TOKENS=1800`), disconnect cancellation, single bounded repair (`VOICE_AUDIO_REPAIR_ENABLED=true`), optional `modifiers` & nullable `estimated_grams`/macros (`portion_specified=false`), and zero audio/transcript persistence or content logging. Kept `POST /api/v1/parse-voice-meal` for backward compatibility and edited-transcript retries.
- [x] Replaced mobile `expo-speech-recognition` / `speechRecognitionService.ts` with `expo-audio` (`~58.0.10`), `expo-file-system` (`~58.0.13`), and `expo-asset` (`~58.0.19`): configured `apps/mobile/app.json` (`enableBackgroundRecording=false`, `enableBackgroundPlayback=false`), added native-module-safe `apps/mobile/src/services/audioRecordingService.ts` (`requireOptionalNativeModule('ExpoAudio')`, `.m4a` AAC recording <=90s / <=10MB, temp cache deletion on upload/cancel/close/unmount), updated `apps/mobile/src/services/voiceFoodLogging.ts` (`parseVoiceAudio`, specificity-preserving `matchVoiceItemsToCatalogue`, `modifiers`, nullable portions), and rewrote `apps/mobile/src/components/VoiceFoodLoggingModal.tsx` into a 5-stage UX (`idle` -> `recording` -> `analyzing` -> `review` -> SQLite confirmation) with `Retry Audio`, editable transcript retry, `Open Food Search`, synchronous `savingRef` lock, and no fake/offline-guessing recovery path.
- [x] Added opt-in human audio evaluation protocol and consent-gated CLI (`docs/AUDIO_VOICE_EVAL_PROTOCOL.md`, `backend/scripts/eval_voice_audio.py`, `--consent-upload` gate) plus mocked test suites (`backend/tests/test_voice_audio.py`, updated `backend/tests/test_timeout_reliability.py`, `apps/mobile/tests/aiRecognition.test.mjs`, `apps/mobile/tests/voiceFoodLogging.test.mjs`) using zero live AI quota.
- [ ] User approves push (`origin/master`), Render backend deployment (`POST /api/v1/parse-voice-audio`), and new Android preview APK build (`versionCode: 2` with `expo-audio` native module) before real-device opt-in audio verification (old APK `versionCode: 1` lacks `expo-audio`).

## Milestone 4E — Final Android Preview APK Preparation — prepared (awaiting EAS build approval)

- [x] Audited Android release configuration across `apps/mobile/app.json`, `apps/mobile/eas.json`, `apps/mobile/package.json`, `apps/mobile/package-lock.json`, and `apps/mobile/src/services/aiFoodRecognition.ts` (application ID `com.bites2go`, EAS project `1e504316-51f2-4b43-ab54-ffcd26d92eba`, preview profile `distribution: internal` / `buildType: apk`, remote signing keystore compatibility, `EXPO_PUBLIC_AI_BACKEND_URL=https://bites2go-api.onrender.com`, zero embedded API keys).
- [x] Bumped `expo.android.versionCode` from `1` to `2` in `apps/mobile/app.json` while keeping `version` at `1.0.0`, and verified `expo-dev-client` (`~58.0.18`) is needed for the `development` EAS profile / `expo run:android` while compiling its release stub (`disableInRelease`) on `--profile preview`.
- [x] Applied Prettier formatting to the 5 flagged files (`VoiceFoodLoggingModal.tsx`, `aiFoodRecognition.ts`, `voiceFoodLogging.ts`, `aiRecognition.test.mjs`, `voiceFoodLogging.test.mjs`).
- [x] Verified offline voice fallback acceptance criteria and added focused unit/regression coverage (`savingRef` rapid-tap confirm guard + offline diary history preservation & idempotency test; production HTTPS backend URL validation & scheme check tests).
- [ ] Run `cd apps/mobile && npx --yes eas-cli build --platform android --profile preview` after explicit release approval (no push, deploy, or EAS build triggered).

## Milestone 4C — Quota-Aware Voice Reliability & Offline Catalogue Fallback — implemented

- [x] Inspected live OpenRouter `/key` (`is_free_tier=true`, `free_model_daily_requests={used:52, limit:50, remaining:0}`) and actual HTTP `429` headers/payload (`X-RateLimit-Limit: 50`, `X-RateLimit-Remaining: 0`, `X-RateLimit-Reset` ms timestamp, `limit_source: openrouter_free_tier_daily`, `metadata.provider_name`).
- [x] Implemented evidence-based `429`/`402` taxonomy (`daily_quota_exhausted`, `burst_rate_limit`, `upstream_provider_saturated`, `rate_limit`) in `backend/app/services/providers/openrouter_provider.py` (`classify_openrouter_rate_limit`) and `gemini_provider.py` (`retry in Xs` extraction).
- [x] Built thread-safe bounded `ProviderCooldownTracker` in `backend/app/services/ai_service.py` + `backend/app/config.py` (`15–60s` burst/upstream, max `300s` daily cap) skipping cooled-down providers with zero wasted HTTP calls, isolating 503 voice fallback from Gemini photo primary, never switching alternative OpenRouter models on account-wide 429s, and surfacing safe `rate_limit_cooldowns` on `/health` and bounded `Retry-After` headers on `/api/v1/*`.
- [x] Added deterministic offline voice catalogue fallback (`matchVoiceTranscriptOffline`) in `apps/mobile/src/services/voiceFoodLogging.ts` and `VoiceFoodLoggingModal.tsx`: retains editable `transcript`, `meal`, and `targetDate` on cloud failure, uses existing `searchFoods`/`scaleNutrients`/`sumNutrients` and `createEntry`, preserves `null` unknown macros without inventing `0`, omits unmatched items cleanly, and requires explicit user confirmation before logging.
- [x] Verified `122/122` backend tests, `166/166` mobile tests, and `0` TypeScript errors cleanly in focused commits on `master` (no push, deploy, Render config change, or APK build).

## Milestone 4B — Fix NVIDIA Voice Timeout & Enforceable Cancellation — implemented

- [x] Diagnosed live HTTP 504 on request `7f59355e` (OpenRouter completing at `50.978s` past `35.0s` server deadline without reaching Gemini fallback): `httpx.Timeout` only bounds per-read idle gaps while OpenRouter streams `200 OK` headers + periodic keepalive chunks, and synchronous `client.post(...)` inside `asyncio.to_thread` could not abort on wall-clock timeout or `cancel_event`.
- [x] Implemented enforceable wall-clock deadlines and genuine socket cancellation in `backend/app/services/providers/openrouter_provider.py` (`_post_with_wall_clock_deadline`, `_strip_hop_and_encoding_headers`), `backend/app/routers/food.py` (`current_request_deadline` ContextVar), and `backend/app/services/ai_service.py`: real HTTP calls now stream via a request-scoped `httpx.Client` with a `0.15s` daemon watchdog closing the TCP socket immediately upon `cancel_event` or wall-clock expiration.
- [x] Benchmarked `nvidia/nemotron-3-ultra-550b-a55b:free` vs `nvidia/nemotron-3.5-lightning:free` across 5 controlled Indian/Hinglish/correction transcripts (`task-6645`, `task-6658`, `$0` cost): kept `nvidia/nemotron-3-ultra-550b-a55b:free` as default pending user choice, documenting accuracy-vs-speed evidence.
- [x] Optimized voice prompt & token budgets (`VOICE_OPENROUTER_MAX_TOKENS=900`, removed redundant transcript echo/null bloat, compact `VOICE_PARSER_SYSTEM_INSTRUCTION`) and tightened voice deadlines (`VOICE_PRIMARY_TIMEOUT_SECONDS=14.0`, `VOICE_SERVER_DEADLINE_SECONDS=32.0`, `reserve_fallback_seconds=14.0`) while leaving Gemini photo configuration completely unchanged.
- [x] Verified with real TCP keepalive/hung socket abort tests, Gzip streaming test, Gemini fallback tests (`115` backend pytest tests total), mobile tests, and TypeScript check (`0` errors). Do not push/deploy or auto-switch production model without approval.

## Milestone 4 — Reliable AI Voice and Image Recognition — implemented

- [x] Inspected live Render deployment (`40762dbc`) and mobile/backend timeout budgets (`45.0s` mobile photo / `40.0s` mobile voice vs `35.0s` server deadline).
- [x] Benchmarked live Gemini and OpenRouter free-tier models cleanly: verified `gemini-3.5-flash` with `ThinkingConfig(thinking_budget=0)` reduces photo inference from ~17.54s to ~2.69s–8.49s, while `nvidia/nemotron-3-ultra-550b-a55b:free` handles complex Indian/Hinglish voice transcripts accurately (`response_format` omitted, text-only).
- [x] Implemented task-specific provider routing in `backend/app/services/ai_service.py` (`DualProviderService`) and `backend/app/config.py`:
  - Voice meal parsing (`POST /api/v1/parse-voice-meal`): primary `openrouter` (`nvidia/nemotron-3-ultra-550b-a55b:free`, `24.0s` socket timeout, `35.0s` server deadline), fallback `gemini` (`gemini-3.5-flash`, `thinking_budget=0`).
  - Photo food recognition (`POST /api/v1/recognize-food` & `/base64`): primary `gemini` (`gemini-3.5-flash`, `thinking_budget=0`, AFC disabled, `1024px@q82` image downscaling), fallback `openrouter` (`nvidia/nemotron-3.5-super-vl:free` + bounded `dots-studio/dots-3-note-preview:free` alternative).
- [x] Hardened OpenRouter & Gemini providers: blocked image routing to text-only models (`error_category="model_vision_unsupported"`), supported `tool_calls[0].function.arguments` extraction alongside JSON blocks, distinguished daily RPD 429 quota exhaustion vs burst RPM rate limits, and classified `MAX_TOKENS` empty responses as `token_budget_exhausted`.
- [x] Expanded `GET /health` with task-specific routing status fields (`photo_*` and `voice_*`) while preserving existing schema fields and suppressing all secret keys.
- [x] Ran bounded live E2E verification (~2 free API calls total): Nemotron voice returned HTTP 200 (4 Indian/Hinglish items, `31.61s`), Gemini photo returned HTTP 200 (`3.60s`, honest empty detection on synthetic image), cost `$0`.
- [x] Expanded backend test suite from 96 to 106 passing unit tests (`backend/tests/test_timeout_reliability.py`, `test_dual_provider.py`, `test_food_recognition.py`, `test_image_processing.py`) and updated `.env.example`, `backend/.env.example`, `backend/README.md`, `TASKS.md`, and `docs/MEMORY.md`.
- [ ] User deploys verified backend commit to Render and unsets legacy `OPENROUTER_MODEL=openrouter/free` override if present (no remote push/deploy or APK rebuild performed in this milestone).

## Recipe Screen Compilation & Mobile Build Fix — implemented

- [x] Identified root cause of TypeScript compilation failure in `apps/mobile/src/screens/RecipeScreen.tsx`: uncommitted working-tree edits introduced duplicate declarations and malformed JSX fragment nesting.
- [x] Cleaned up `RecipeScreen.tsx` with clear file header documentation, removed duplicate declarations, and simplified search match condition.
- [x] Preserved recipe creation, editing, ingredient selection from unified foods and custom foods, dynamic nutrition calculations (`recipeNutrition`), and SQLite persistence.
- [x] Verified full TypeScript compilation: `npx tsc --noEmit --project apps/mobile/tsconfig.json` passed with 0 errors.
- [x] Ran mobile test suite: `npm test --prefix apps/mobile` passed 163/163 unit tests.
- [x] Validated Android bundling: `npx expo export --platform android` succeeded bundling 1,377 modules and generating release Hermes bytecode bundle `entry-*.hbc`.

## Gemini API Transient Resilience & Automatic Retry — implemented

- [x] Inspected FastAPI Gemini food recognition service, Google GenAI SDK (`google-genai==2.34.0`), timeout settings, and exception hierarchies.
- [x] Implemented bounded automatic retry executor (`_execute_with_retry`) in `GeminiService` using exponential backoff with jitter (`tenacity==9.1.4`), retrying transient failures (HTTP 429, 500, 502, 503, 504, and transport timeouts) with a maximum of 2 additional attempts (3 total).
- [x] Enforced strict non-retry policy for permanent failures: authentication errors (401), invalid requests (400), permissions (403), missing resources (404), configuration errors, and malformed model JSON outputs fail immediately on attempt 1.
- [x] Bounded per-attempt timeouts to 12.0s and configured `retry_options=None` in `GenerateContentConfig(http_options=...)` to prevent multiplying requests or stacking SDK internal retries.
- [x] Applied bounded retries across food photo recognition (`recognize_food`) and evaluated voice meal parsing (`parse_voice_meal`), ensuring responsive real-time voice logging.
- [x] Added structured audit logging for every attempt: operation name, attempt number, elapsed time per attempt, transient error details, sleep duration, and final status without logging API keys, image bytes, or secrets.
- [x] Returned structured, safe HTTP error responses with status codes (504 Gateway Timeout, 503 Service Unavailable, 429 Rate Limit) and headers (`Retry-After`, `X-Error-Category`) without exposing internal stack traces.
- [x] Guarded mobile UI (`AIFoodScannerModal.tsx`, `VoiceFoodLoggingModal.tsx`) against duplicate diary logging on retry and ensured loading indicators reset properly with actionable retry prompts.
- [x] Expanded backend test suite from 28 to 43 tests covering transient 504/503/429/timeout successes on retry, exhausted retries, immediate permanent failures, and endpoint responses.
- [x] Expanded mobile unit test suite from 161 to 163 tests covering structured 504/503 error handling across photo and voice parsing.

## Voice-Based Food Logging — implemented

- [x] Implemented production-quality voice food logging pipeline supporting spoken natural language meal descriptions.
- [x] Configured native speech-to-text with `expo-speech-recognition@58.0.1` compatible with Expo SDK 58 and Android permissions (`RECORD_AUDIO`, `androidSpeechServicePackages`).
- [x] Built safe platform adapter (`speechRecognitionService.ts`) preventing `Cannot find native module 'ExpoSpeechRecognition'` runtime crashes in stock Expo Go or unlinked environments via `requireOptionalNativeModule` and `isRunningInExpoGo()`.
- [x] Implemented graceful fallback UI banner and keyboard dictation guidance in `VoiceFoodLoggingModal.tsx`, preserving full transcript editing, Gemini natural language parsing, catalogue matching, and atomic SQLite diary logging across all environments.
- [x] Configured `eas.json` with development and preview profiles for APK distribution.
- [x] Built FastAPI backend endpoint `POST /api/v1/parse-voice-meal` using Google GenAI SDK with structured schema validation (`VoiceMealParseResponse` and `ParsedVoiceFoodItem`).
- [x] Engineered comprehensive prompt interpretation: multi-item dish separation (e.g. rotis, dal, sabzi, coffee), colloquial measures (bowls, handfuls, slices, cups), in-flight speech self-corrections ("one roti, actually make that two"), preparation methods, and raw vs cooked weights.
- [x] Integrated client matching against the 1,411-food unified catalogue, preserving dataset-first priority (Kaggle tier 1 > Built-in tier 2 > Custom tier 3) and nutrition provenance metadata.
- [x] Created accessible, high-contrast modal (`VoiceFoodLoggingModal.tsx`) with clear states: idle, listening with live volume meter, editable transcript text area, processing indicator, and candidate review screen.
- [x] Added candidate editing: portion adjustments with live Atwater-consistent macro recalculation, alternative catalogue food selection, toggle between verified catalogue data and Gemini AI estimate, and manual item addition/deletion.
- [x] Ensured atomic diary persistence to SQLite via `diary.saveAll(entries)` with rollback on write failures.
- [x] Integrated "Log Meal with Voice" entry point into `FoodSearchScreen.tsx` (`SearchHeader`).
- [x] Created comprehensive test suites: backend pytest suite expanded from 19 to 28 tests; mobile test suite expanded from 154 to 161 tests covering natural language interpretation, catalogue matching, portion scaling, and atomic error recovery.
- [x] Passed 100% of quality gates: 161 mobile unit tests pass, 28 backend tests pass, TypeScript compiles with 0 errors, ESLint passes with 0 warnings/errors, Prettier format check passes, Expo Doctor passes 20/20 checks, Metro Android release export succeeds (1,376 modules), and security scan passes with 0 pattern findings.

## VirtualizedList Performance & Large Catalogue Optimization — implemented

- [x] Investigated React Native VirtualizedList slow update warnings (`contentLength: 3520, dt: 1106`, `contentLength: 13102, dt: 707`).
- [x] Identified root causes: unwindowed rendering of all 1,411 catalogue entries simultaneously in FlatList, unstable inline `onPress` callback recreation defeating `React.memo(FoodChoice)` on every keystroke, and unmemoized food filtering in `RecipeScreen.tsx`.
- [x] Created module-scope memoized `FoodSearchRow` in `FoodSearchScreen.tsx` with stable `onSelect` callback reference, guaranteeing zero row re-renders across search input keystrokes.
- [x] Implemented incremental windowing (initial 40 items + 40 item batch pagination via `onEndReached`), reducing initial catalogue mount payload by 97% while keeping all 1,411 foods fully searchable and discoverable.
- [x] Tuned FlatList virtualization parameters: `initialNumToRender: 10`, `maxToRenderPerBatch: 10`, `windowSize: 5`, and `onEndReachedThreshold: 0.5`.
- [x] Optimized `RecipeScreen.tsx` and `MyFoodsScreen.tsx` with memoized available food collections, O(1) ingredient Set membership lookups, and stable callbacks.
- [x] Preserved dataset-first search ranking (Tier 1 Kaggle foods rank first for equal scores), offline SQLite persistence, and Android keyboard-focus fix.
- [x] Added automated regression & benchmark test suite (`apps/mobile/tests/virtualizedListPerformance.test.mjs`); all 154 mobile tests passed, 19 backend tests passed, TypeScript, ESLint, Prettier, Expo doctor (20/20 passed), Android release export, and credential security scan passed with 0 findings.

## Nutrition Data Quality & Staple Foods Provenance — implemented

- [x] Audited all 1,411 foods in unified catalogue (894 built-in + 517 Kaggle items) across 7 food categories for nutritional accuracy, physical bounds, Atwater factor consistency, and source provenance.
- [x] Produced comprehensive `docs/NUTRITION_DATA_QUALITY_REPORT.md` documenting methodology, authoritative data sources (USDA FoodData Central, ICMR-NIN IFCT 2017), physical bounds checks, and Atwater tolerance bands.
- [x] Upgraded 68 high-priority staple foods in `apps/mobile/src/data/foods.ts` to `verified` (42 items with explicit USDA FDC ID or ICMR-NIN IFCT 2017 code) or `estimated` (26 composite dishes with IFCT recipe formulation IDs).
- [x] Catalogue-wide provenance upgraded from baseline 36 verified (2.6%), 14 estimated (1.0%), and 1,361 illustrative (96.5%) to 78 verified (5.5%), 40 estimated (2.8%), and 1,293 illustrative (91.6%).
- [x] Preserved baseline items 0–11 invariants strictly (including `rice-cooked` at 150 kcal and undefined `servingGrams`) ensuring zero regressions across existing library, calendar, and diary test suites.
- [x] Added rigorous automated verification suite (`apps/mobile/tests/nutritionAccuracy.test.mjs`) testing all 894 built-in items for physical bounds, verified/estimated provenance metadata, and representative batch 2 staple accuracy.
- [x] Verified full test suites: all 150 mobile tests passed, 19 backend tests passed, TypeScript, ESLint, Prettier, Expo doctor (20/20 passed), Android release export bundled, and credential scan passed with 0 findings.

## Kaggle Dataset Integration (`adilshamim8/daily-food-and-nutrition-dataset`) — implemented

- [x] Inspected Kaggle dataset v2: 651 raw records (1 header + 651 data rows), 12 columns, fixed 6 anomalous lines with unquoted commas.
- [x] Verified dataset provenance & license: authored by Adil Shamim (`adilshamim8`), synthetic simulation dataset, strictly marked `status: 'illustrative'` across all imported items.
- [x] Built deterministic preprocessing and validation pipeline (`scripts/import_kaggle_dataset.py`) converting records to referenceGrams=100 with physical macronutrient density and energy density bounds.
- [x] Quarantined Line 486 (`Corn Nuts (1 oz)`) violating physical macronutrient bounds (102.1g macros per 100g).
- [x] Merged 58 redundant internal duplicate rows within Kaggle dataset, yielding 592 unique items.
- [x] Cross-catalogue deduplication against 894 built-in foods: 75 certain merges (preserving stable original IDs like apple, banana, almonds), 40 distinct varieties/preparations kept separate (e.g. 2% milk vs whole milk), 35 ambiguous matches with >35% calorie variance kept separate.
- [x] Generated `apps/mobile/src/data/kaggleFoods.ts` (517 new items with `kaggle:` prefix) and `apps/mobile/src/data/unifiedFoods.ts` (1411 items total).
- [x] Implemented dataset-first search ranking in `src/domain/food.ts`: Tier 1 Kaggle (+0.4 bonus), Tier 2 Built-in (+0.2 bonus), Tier 3 Custom/Recipes (+0.0 bonus).
- [x] Updated `FoodSearchScreen.tsx`, `RecipeScreen.tsx`, and `LibraryControls.tsx` to search `unifiedFoods` while maintaining memoized `SearchHeader` to avoid keyboard blur regression.
- [x] Created comprehensive unit test suite (`apps/mobile/tests/kaggleSearch.test.mjs`) covering all 10 validation requirements; all 149 mobile tests pass.
- [x] Documented full metrics, methodology, and provenance in `docs/KAGGLE_IMPORT_REPORT.md`.

## Expanded Food Catalogue & Food Images — implemented

- [x] Substantially expanded built-in food database to 894 items across Indian staples, regional Maharashtrian dishes, dals, sabzis, South Indian breakfast, street food, snacks, sweets, international fruits, vegetables, proteins, dairy, grains, fast food, beverages, and ingredients.
- [x] Preserved baseline items 0-11 (`rice-cooked`, `rice-raw`, `roti`, `moong`, `chickpeas`, `milk`, `curd`, `banana`, `apple`, `almonds`, `oats`, `paneer`) for strict backward compatibility with existing tests.
- [x] Sourced, optimized, and bundled 32 CC0/Public Domain/CC-BY food photos (34 total photos with apple and banana) at 240x240 JPEG (~400 KB total) with full license attribution in `assets/food/README.md`.
- [x] Upgraded image registry (`src/data/foodImages.ts` and `src/components/FoodImage.tsx`) supporting 34 photographic assets, imageKey resolution, and 12+ category SVG fallback icons/badges (`AppIcon`).
- [x] Implemented enhanced scored search in `src/domain/food.ts`: exact match, prefix match, alias/regional match, multi-word matching, and relevance ranking.
- [x] Enhanced search results UI (`FoodChoice`) displaying thumbnails/category badges, short serving descriptions, calories, and macros breakdown (`P · C · F`).
- [x] Added interactive common serving size chips to food detail (`FoodSearchScreen.tsx`) with immediate live recalculation.
- [x] Implemented idempotent SQLite catalogue repository (`src/storage/catalogRepository.ts`) managing `bites2go.catalog.v1` metadata, preserving user custom foods, recipes, favourites, and immutable diary history.
- [x] Verified full test suites: 119 mobile tests passed, 19 backend tests passed, TypeScript, ESLint, Prettier, Expo doctor (20/20 passed), Android export, and credential security scan (0 findings).
- [ ] User verifies food search, image display, and portion chips on physical Android device.

## My Meals & Recipes — implemented

- [x] Inspect/reuse recipe/library/diary schemas and snapshots on clean master 1088789808dd7777c3739058cf30f3ca80630e83; baseline 96 tests passed.
- [x] Expose My Meals with create/view/edit/delete, ingredient/whole/per-serving nutrition and explicit Log Meal actions.
- [x] Default recipe selection to one serving with fractional/multiple serving entry; preserve date/category and one combined diary snapshot.
- [x] Extend nutrition, serving-default, retry/deduplication, history/insights and SQLite close/reopen coverage; 22 targeted and 98 full tests pass.
- [x] Final types/lint/format, Doctor 20/20, public configuration and Android export pass; no dependencies, schema, AI or cloud changes.
- [x] Document workflow, architecture and current results; audit still FAILS unchanged (3 high/5 low), production blocker retained.
- [ ] Physical Android My Meals acceptance checklist in TEST_PLAN.md. No native verification claimed.

Stop after My Meals. AI food recognition remains deferred.

## Stage 11: development acceptance passed; production release blocked

- [x] Verify clean master/origin at 369d562b7bfeee014810d9236f1097bef2d2ce85 and rerun baseline 93 tests/checks.
- [x] Trace both advisories and all eight audit rows; verify installed versions, tooling call sites and compatible patch availability.
- [x] Fix diary uncertain-write exit reconciliation, repeated validation scans and checkpoint revision regression; remove raw splash errors.
- [x] Verify 96 tests, expanded existing contrast assertions, types/lint/format, Doctor 20/20, config, Android export and real local SQL policy tests.
- [x] Review current/history/export credential patterns and document findings, privacy/accessibility limits and release checklist.
- [ ] Resolve audit: 3 high / 5 low remain; no supported compatible patch verified. This remains a production release blocker; the user explicitly permits the Stage 11 development commit.
- [ ] Physical Android, signed build/install and release privacy checklist in RELEASE_READINESS.md.
- [x] Final development acceptance: repeat all required checks, local SQL and credential scan; audit fails unchanged and is explicitly excepted for the development commit only. Commit/push outcome is verified in the final report. Stop before another stage.

## Current task: Stage 10 Nutrition Insights

- [x] Verify clean master/origin at 703b25ae1c5a726491d880f4955de2944ece3475 and run baseline suite: 79 tests passed.
- [x] Inspect authoritative snapshots, date helpers, historical targets, weight/library/storage/theme and navigation conventions.
- [x] Add offline Insights from Progress with 7/30-day/custom ranges, daily nutrition/targets, nutrient trends, averages, consistency, observations and actual weight context.
- [x] Document and share per-nutrient eligibility, unknown values, limited meal coverage, today exclusion, inclusive tolerance and historical weight-goal limits.
- [x] Verify 93 tests, types, lint, formatting, Doctor 20/20, configuration, Android export and existing SQL integration checks; review unchanged audit findings.
- [x] Update feature/product/architecture/design/test/memory documentation. No new dependencies, migrations or cloud activation.
- [ ] Physical Android acceptance (themes, scrolling, keyboard/Back, large text, TalkBack and offline regressions) in Test Plan.
- [ ] User review and Stage 10 acceptance before authorizing Stage 11 consolidated quality/security. Do not start Stage 11 automatically.

## Current task: Stage 9 backend foundation (no configured cloud)

- [x] Verify clean master and remote at 6f6794add78f9017089a9f100baaaee9e0b48c53; inspect local data and project instructions.
- [x] Compare current official Supabase/Firebase documentation, select Supabase and document free limits, portability and operational responsibilities.
- [x] Implement fail-closed public configuration and honest offline Profile status; preserve existing local providers/write paths.
- [x] Add account-consented diary sync planning, guarded merge/upload contract, conflicts/tombstones/retries and isolated checkpoint repository, disconnected from live app data.
- [x] Add PostgreSQL migration and verify ownership/RLS/RPC in a disposable real database with synthetic identities.
- [x] Verify 79 tests, types, lint, formatting, Doctor 20/20, public config and Android bundle; review unchanged 5 low/3 high audit.
- [x] Document backend setup, missing implementation gates, privacy, export/deletion, architecture and test limitations.
- [ ] Configure a development Supabase project and live SDK authentication/secure session storage (not available in this task).
- [ ] Implement/test real transport, consent/conflict UI and local transactional coordinator before any uploads; verify two real accounts and anonymous/expired sessions.
- [ ] Android offline/regression/accessibility acceptance; later live cloud acceptance.
- [ ] User review; do not begin Stage 10.

## Current task: Stage 8 custom foods, recipes and favourites

- [x] Verify clean synchronized master at e0c0ffee137392ae893b95da5375d3fedbbc3525 and inspect repository/storage/calculation/theme conventions.
- [x] Implement validated custom-food CRUD, estimate labels, nullable nutrients and searchable brands/descriptions.
- [x] Implement built-in/custom ingredient recipe editing, measured yield/servings, shared calculations and incomplete-nutrient handling.
- [x] Add persistent unique favourites, actual diary-derived recents and confirmed grams/servings quick-add with meal/date preservation.
- [x] Add isolated additive SQLite library initialization, atomic source/favourite cleanup, retry/stale protection and unchanged diary snapshots.
- [x] Verify 66 tests, types, lint, formatting, Doctor 20/20, public config and Android export; inspect unchanged 5 low/3 high audit findings.
- [x] Document product, architecture/storage/calculation, design, security and testing decisions and limitations.
- [ ] User verifies Stage 8 Android restart, CRUD/history, keyboard/Back, all themes and accessibility scenarios in Test Plan.
- [ ] User review before Stage 9; do not begin it automatically.

Older stage sections below are historical records, not current scope restrictions or new authorizations.

## Current task: Stage 7 weight, goals and BMI

- [x] Verify clean synchronized master at 2214b4861f0522be4f1c806d384f112d49008a99 and inspect project/storage/theme conventions.
- [x] Implement validated kg records with local dates, unique dates/IDs, edit/delete confirmation, chronological history and actual-point chart.
- [x] Implement effective-dated calorie/protein/carbs/fat targets and consume them in Home, Diary and Calendar without rewriting historical targets or nutrition snapshots.
- [x] Add cm height, numeric adult BMI and explicit gain/loss/maintenance weight goals with safe missing/equal-baseline cases.
- [x] Add isolated versioned SQLite KV persistence, retry/stale-write checks and non-destructive empty initialization.
- [x] Verify 51 tests including SQLite close/reopen; typecheck, lint, formatting, Doctor 20/20, config and Android export.
- [x] Update product, design, architecture/migration, security, test and memory documentation; disclose unchanged audit findings.
- [ ] User verifies Stage 7 on Android (restart, keyboard/Back, historical CRUD/goals, narrow layout, all themes and TalkBack).
- [ ] User review before Stage 8; do not start it automatically.

## Current task: visual redesign and appearance

- [x] Verify clean master at Stage 6 commit 1f61e752422f2c13b251d05ff24326caaa360d44.
- [x] Implement Vibrant Food App styling across Home, Search/details, Diary, Calendar, Profile and shared navigation/dialogs.
- [x] Add persistent Light/Dark/System preference, default System, with immediate updates and visible storage errors.
- [x] Add stable-ID local CC0 apple/banana photos and shared missing-image fallback without modifying food values or diary schema.
- [x] Verify 37 unit tests, TypeScript, lint, formatting, Doctor 20/20, public config and Android export during implementation.
- [x] Document design, storage, photo licensing, tests and unchanged audit advisories.
- [ ] Android visual/accessibility, restart, System-switch and regression acceptance by the user.
- [ ] User review; do not begin Stage 7.

## Current task: Stage 6 calendar and history

Stage 5 save/restart/edit/delete was verified on Android by the user. This does not establish calendar or accessibility verification. Earlier stage sections below are historical; Stage 7 is not authorized.

- [x] Verify clean synchronized master 5a9f96b and inspect dates, storage and navigation.
- [x] Replace Calendar placeholder with Monday-first month navigation, selection, Today and actual-entry markers.
- [x] Reuse historical diary summaries/meals/Add Food/edit/delete with selected-date preservation.
- [x] Index loaded entries by date without schema migration, duplicate records or additional navigation reads.
- [x] Verify 31 tests, types, lint, formatting, Doctor, config and Android export; disclose audit findings.
- [x] Document date/query strategy and limitations.
- [ ] User verifies Stage 6 on Android: calendar layout, selection, scrolling, Back, historical flows and accessibility.
- [ ] User review before Stage 7; do not start it automatically.

## Current task: Stage 5 local persistent diary

The explicit request supersedes older Stage 5 Auth/Supabase dependencies. Work is directly on master. Historical checklists below do not authorize further work.

- [x] Verify clean synchronized master and inspect existing code/docs/dependencies.
- [x] Add Expo-compatible local SQLite storage behind a validated repository with failure-safe serialized writes.
- [x] Save food/meal/date/portion snapshots, prevent duplicate retry entries, preserve unknown nutrients.
- [x] Show real-entry totals and honest empty states; no sample meals counted.
- [x] Add portion editing/cancellation, confirmed deletion and minimal diary-day navigation.
- [x] Verify 23 automated tests, types, lint, formatting, Doctor, public config and Android bundle export; disclose existing audit findings.
- [x] Document schema, local dates, failure handling, migration and privacy limitations.
- [ ] Verify native SQLite persistence after closing/reopening on Android, plus the manual Test Plan scenarios.
- [ ] User review and explicit authorization before Stage 6. No Stage 6 implementation.

## Current workflow and integration

Direct-to-master development is now the default under AGENTS and RULES; earlier branch-only/no-merge instructions are historical. The fetched remote master at 845b953 already contained SDK 58 (64e5f33) and the first dashboard (2c548e2). Integration preserves that merge and adds the dependent visual refinement (2e81e27) and local food search (b9f76f3) without cherry-picking or duplicating commits. The merge was conflict-free and its application tree matched the Stage 4 branch.

The user reports manually verifying Stage 4 on an Android phone. This is user-reported acceptance, not a new agent-run device test; device/OS and individual accessibility scenarios were not supplied. No next development stage is authorized. Wait for the next explicit instruction.

## Current Stage 4 status — 2026-10-30

Stage 4 is the user-authorized **offline food-search and portion-preview foundation**, superseding the earlier Stage 4a/4b backend scope. Historical stage notes below are retained as history, not current instructions. No backend/authentication/persistence has been implemented. Stop before Stage 5.

Status as of 2026-10-30. Stage 2 is authorized; Stage 3 awaits review. A stage is complete only with documented evidence. Each stage can contain multiple small reviewed tasks; do not implement a stage's entire feature list in one generation.

- [x] **Stage 1 — Foundation.** Inspect complete project workspace and Git/tools; preserve existing state; document product, architecture, design, tests, security, research, decisions, rules and GitHub process; review links/consistency. No app implementation, commits or pushes.
- [x] **Approval gate.** User reviews Stage 1 and approves Stage 2. No dependent implementation before approval.
- [ ] **Stage 2 — Minimal Expo application.** Depends on approval. Acceptance checklist below; no backend/services needed.
- [ ] **Stage 3 — UI prototype.** Depends on 2. Build dashboard and five-tab navigation in separate tasks using labeled synthetic data. Acceptance: Design tokens consistent, Add Food prototype reachable, empty/partial/error states and small-screen/TalkBack checks recorded; no fake persistence claim.
- [ ] **Stage 4a — Data and backend decisions.** Depends on 3. Approve source coverage/rights matrix, runtime versions, Auth plan and environment approach. Acceptance: every MVP food category has lawful source or explicit documented gap; blockers resolved before catalog publication; no unverified values.
- [ ] **Stage 4b — Nutrition foundation.** Depends on 4a. Initialize modular FastAPI/Pydantic, schema/migrations and read-only catalog/search, serving conversions and deterministic engine. Acceptance: calculation/unit/import tests, source/missingness metadata and shared preview fixtures pass; dependencies locked; no private data until RLS gate.
- [ ] **Stage 5a — Auth and isolation.** Depends on 4b and authorized Supabase environment. Acceptance: JWT validation, secure session flow, private-table RLS/grants and restricted write function pass two-user/anonymous/direct-API tests.
- [ ] **Stage 5b — Persistent logging.** Depends on 5a. Add/edit/delete four meal categories, quantity previews, snapshots, daily totals and historical dates. Acceptance: restart/refetch works; no duplicate retry or silent concurrent overwrite; old catalog versions stable; network errors preserve drafts.
- [ ] **Stage 6 — Calendar/history.** Depends on 5b. Monthly navigation, diary date selection, completeness and simple logging/goal streak calculations. Acceptance: product rule review completed, timezone/leap/gap/backfill/deletion cases pass. Goal streak shows not evaluable until goals exist; use synthetic target fixtures for tests.
- [ ] **Stage 7 — Weight and goals; MVP checkpoint.** Depends on 6. Manual nutrition targets, effective dates, BMI, dated weights and trends. Acceptance: gain/loss/maintenance/zero targets handled, weekly averages show sample counts; end-to-end Android MVP manual journey and privacy gates pass. No AI dependency.
- [ ] **Stage 8 — Custom and reusable foods.** Depends on MVP. Custom foods, recipes/yields/versions, favorites, saved meals and copy flow in separate tasks. Acceptance: ingredient arithmetic, private ownership, stable history and independent idempotent copies verified.
- [ ] **Stage 9 — Nutrient insights.** Depends on 8 and sufficient licensed nutrient data. Acceptance: data-coverage limitations, preferences/exclusions, calorie context and optional budget respected; no deficiency diagnosis.
- [ ] **Stage 10 — AI assistance.** Depends on reliable MVP, source mapping, explicit processing/privacy/budget approval and provider re-evaluation. Implement adapter/evaluation, then photo review and later text logging as separate tasks. Acceptance: benchmark recorded, uploads cleaned up, estimates editable, no save without confirmation, manual fallback and spend limits tested. Voice/assistant remain optional later tasks.
- [ ] **Stage 11 — Consolidated quality/security.** Depends on selected release scope. Acceptance: automated checks, RLS, dependency review, network failure, accessibility, privacy/retention/delete/export and agreed performance checks recorded; no unresolved critical/high security/data-loss issues. Testing also occurs in all earlier stages.
- [ ] **Stage 12 — Android release preparation.** Depends on 11 plus authorized build configuration. Acceptance: installable APK built and installed on a recorded device/OS, signing/config/secrets reviewed, release procedure and limitations documented. Store publication requires separate approval.

## Exact next implementation task: Stage 2

Create one minimal Expo TypeScript app in `apps/mobile/`, keeping root documentation intact. Use npm and a lockfile; no root workspace tooling, backend, auth, real food dataset or AI. Use one presentational landing screen to demonstrate the theme, not a functional dashboard.

Acceptance criteria:

- [x] Reinspect Git/user changes and read RULES, Memory, Architecture and Design before scaffolding.
- [ ] Recheck official Expo SDK/device compatibility and package Node engines. Record exact Expo, React Native, React, Node and npm versions. Current docs show SDK 58 versus Expo Go SDK 57 transition; choose deliberately.
- [x] Initialize only `apps/mobile/` with TypeScript and strict checking; no nested `.git` repository. Keep a single root Git history and review generated files.
- [x] Add reusable color, typography, spacing and radius tokens; minimal accessible screen shows Bites2Go and one clearly labeled demo action. Respect safe area and font scaling.
- [x] Configure actual npm `lint` and `typecheck` scripts; run them successfully along with Expo Doctor. Record exact commands/output; fix relevant failures.
- [ ] Launch on a recorded Android device or emulator and verify screen, interaction and reload without crash. Expo Go is acceptable for this small first task when SDK-compatible. A web preview alone does not satisfy Android acceptance.
- [x] Add no services, secrets, API calls, paid builds or feature-wide implementation. Do not create external accounts. If no Android device/emulator is available, report Stage 2 incomplete with that exact blocker rather than claiming launch success.
- [x] Update README with working install/run/check commands, chosen launch route, limitations and reproducible setup; update Memory and this checklist with actual evidence.
- [x] Review diff and generated dependency files for secrets/unrelated changes. Follow the user's then-current commit authorization and GitHub workflow; absence of a remote does not justify invented push success.

Android path recommendation: use a physical device with matching Expo Go for Stage 2 if available; otherwise arrange local SDK/emulator setup after agreement. Own development builds and APK signing remain later bounded tasks.

## Stage 2 implementation — 2026-10-30

User approved Stage 2 in the current request. Implemented in `apps/mobile/` (supersedes the earlier `mobile/` proposal). Single empty diary screen, theme tokens, strict TypeScript, safe areas and a clearly labeled placeholder Add Food alert. No real nutrition data or services.

Verified: typecheck, lint, formatting, one AA contrast test, Expo Doctor 21/21, public Expo config and Android Hermes bundle export passed. `npm start -- --localhost` started Metro at port 8081; its status endpoint returned `packager-status:running`. This verifies development-server startup, not on-device rendering. No Android execution: adb/emulator unavailable on PATH, Android SDK variables unset and standard local SDK adb absent. Device layout, TalkBack and font scaling still require manual verification.

Installed: Expo 57.0.31, React Native 0.86.3, React 19.2.3, safe-area-context 5.7.0, TypeScript 6.0.3, ESLint 9.39.5/config-expo 57.0.2, Prettier 3.9.10, Expo Doctor 1.21.5. Node 22.23.2/npm 10.9.8. Lockfile records transitive versions. SDK 57 follows current Expo Go transition guidance: https://docs.expo.dev/get-started/create-a-project/ . No navigation library needed yet.

Known issues: npm audit retains 8 transitive advisories (5 low, 3 high) involving Expo tooling's deepmerge/zod chain after compatible `npm audit fix`; forced remediation proposes incompatible Expo 51 downgrade and was not applied. Resolve/reassess before release. Expo-selected ESLint 9 emits an upstream support warning; retain compatibility pending supported SDK upgrade. The Node contrast test emits a module-type detection warning but passes. No claim of production security readiness.

Next: review Stage 2 and verify the screen on Android before Stage 3. Stage 3 has not begun.

- [x] Mobile foundation and developer checks implemented and verified.
- [ ] Android device launch, layout and interaction verification (tooling/device unavailable).
- [ ] Review unresolved dependency advisories before release.

## SDK 58 compatibility follow-up

- [x] Create codex/expo-sdk-58 from clean master f75c4f3 and align dependencies through Expo.
- [x] Verify types, lint, formatting, contrast test, config, Doctor and Android bundle export.
- [x] Compare fresh audits before/after; unchanged 8 advisories remain documented in Test Plan.
- [x] Update SDK versions and Android LAN preview instructions.
- [ ] User verifies physical Android preview with SDK 58 Expo Go, layout, Add Food alert and reload.
- [ ] Review upgrade branch before any merge; master unchanged. Stage 3 remains deferred.

## Stage 3 implementation checklist

- [x] Branch from verified clean SDK 58 commit 64e5f33.
- [x] Home summary, macros and four meals with labeled demo data and empty states.
- [x] Five Expo Router tabs; sample Diary and explicit unfinished sections.
- [x] Pure preview totals/progress, five passing tests and developer/build checks.
- [x] Fix preview wording and verify UTF-8 source without replacement characters.
- [ ] Physical Android, TalkBack and large-text visual/navigation verification.
- [ ] User review before Stage 4; no merge into master.

## Stage 4 local foundation checklist

- [x] Verify clean approved Stage 3 commit 2e81e27 and create codex/stage-4-food-search.
- [x] Add 12 explicitly illustrative foods with provenance, preparation, per-100 g values and nullable fiber.
- [x] Connect Add Food to local search/detail/portion preview; retain originating meal and draft within flow.
- [x] Verify search/scaling/draft logic with 10 passing tests and types/lint/Doctor/config/Android export.
- [x] Reconcile roadmap and document source/precision/persistence limitations.
- [ ] Verify actual Android keyboard, Back, TalkBack, font scaling and visual layout.
- [ ] User review before Stage 5. Production catalog licensing and backend/auth isolation remain prerequisites to persistent logging.

- [x] Record user-reported Stage 4 Android verification.
- [x] Integrate completed dashboard refinement and food search on master without duplicate commits.
- [x] Establish permanent direct-to-master rules; no new feature branch or PR.
- [x] Rerun integrated master checks: types, lint, formatting, 10 tests, Doctor, config and Android export; disclose unchanged audit findings.

## Stage 11 dependency follow-up

- [x] Rerun audit/tree and official registry/advisory checks; all eight affected rows documented in RELEASE_READINESS.md.
- [x] Verify latest stable SDK/CLI and transitive range limitations; no safe supported patch found, dependencies unchanged.
- [x] Rerun 96 tests, types/lint/format, Doctor 20/20, public config and Android export; verify affected libraries absent from this export map.
- [x] Hash-check preservation of existing Stage 11 work and document mitigations without claiming remediation.
- [x] User supplied explicit development-only acceptance criteria and conditional commit/push authorization after investigation. Public-release/device gates remain pending.

## R2/U1 photo cancellation — 2026-11-14

Validated locally: Cancel previously ignored taps during analysis; hidden/unmounted scanner requests could complete into stale state. Scanner openings now own separate state, abort on close/unmount/retry, ignore late results and permission/picker callbacks, and clear previous candidates before retry. Both upload methods accept cancellation, retain bounded timeouts and replace raw backend errors with safe status messages and existing request references. Themed error surface, selectable/announced errors and 48dp Cancel control added. No dependencies, routing, diary or nutrition changes.

Tests: 18 targeted and 182 full mobile tests passed; types, lint (after lifecycle correction), formatting and Doctor20/20 passed. Backend unchanged; no live AI, APK build, push or deploy. Native screen interaction remains untested; next priority is Android close/reopen/retry and picker-dismissal acceptance with approved diagnostics. Existing dependency-audit release blocker remains. All 23 preexisting files checksum-preserved. Owner: Codex. Scope: photo lifecycle only; rollback: revert this focused commit. Commit: resolve via git log for this section.

Phase 1A recovery: interrupted scanner work recovered and final lifecycle lint issues resolved. Added image-picker double-tap guard and a regression rejecting late responses even if transport ignores abort. Final types/lint/format and Doctor20/20 passed. Focused local commit only; Phase 1B and later phases not started. Device failure screenshots and supplied Render successes are not correlated; no diagnosis claimed.

## Phase 1B photo evidence and transport fix — 2026-11-14

Verified latest EAS preview6447f478 (1.0.0/code2, source1f8a11c) predates Phase1A; installed APK unknown (no adb device). Render auth unavailable; supplied backend successes remain uncorrelated. Fixed reproduced plain-Error leakage and false timeout classification for unsolicited native AbortError. Both transports tested:22 targeted/186 full mobile tests, types/lint/format, Doctor20/20 pass. No live inference/push/deploy/build, dependency or diary change. All23 existing modified files preserved. Physical acceptance pending; exact protocol and secure Render setup in docs/PRODUCT_COMPLETION.md. Phase1C not started.

## Device-acceptance release preparation

Prepared1.0.0/code3, same com.bites2go/EAS project, remote signing source and explicit preview backend URL. 186 tests/types/lint/format/Doctor20/20/config/local Android export pass; export credential-pattern scan zero. No cloud build/push/deploy. Preserved23 user edits. Build source must explicitly review the uncommitted package/lock pair; signing/installed-version continuity and final APK secrets scan remain gates. See docs/DEVICE_ACCEPTANCE_RELEASE.md for exact upgrade and acceptance instructions.

## Final preview blockers

Reviewed and included the existing Expo58-compatible package/lock pair unchanged; isolated clean offline npm ci succeeds(800packages), Expo dependency check and npm ls pass. Public EAS default signing metadata obtained; device APK certificate comparison remains pending. Render now200 twice, self-reported1f8a11cf and no X-Request-ID: R1 tracing deployment still needed for correlation. Existing23 file contents preserved;21 unrelated edits remain uncommitted. Exact approval-gated push/clean-checkout/build/install sequence and certificate fingerprint recorded in docs/DEVICE_ACCEPTANCE_RELEASE.md. No push/deploy/build or credential change.

## First-attempt photo milestone

- [x] Separate bounded backend wake/readiness from single image inference; cancellable Connecting/Analyzing states.
- [x] Add photo-only120s bypass after two primary timeouts; retain quota checks, fallback deadlines and recovery.
- [x] Validate192 mobile/133 backend tests, types/lint/format, Doctor20/20 and local Android export.
- [ ] Approve/deploy backend and approve new preview build above code3; verify production timing and repeated first scans after idle. Status: partially validated; screenshot request remains uncorrelated. See PRODUCT_COMPLETION for evidence/rollback/acceptance.
