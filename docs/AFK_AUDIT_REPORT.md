# Bites2Go — Production-Readiness and Android Reliability Audit Report

**Date:** 2026-10-31  
**Repository:** `C:\Users\Asus\Music\Bites2Go`  
**Branch:** `master`  
**Latest Baseline Commit:** `f11c70304f26857fde2a6344d8e09ee2f0f1954f` (`fix: correct AI food diary snapshot validation`)  
**Audit Scope:** Production-readiness, Android reliability, Gemini AI security boundaries, physical device networking, SQLite persistence integrity, lifecycle error recovery, and release configuration.

---

## 1. Verified Architecture & Current State

### Mobile Architecture (`apps/mobile`)
- **Runtime:** React Native 0.88.1, React 19.3.0, Expo SDK 58.0.21.
- **Data Persistence:** Authoritative offline-first SQLite KV store (`expo-sqlite/kv-store`). No external network dependency is required for core food logging, custom food/recipe management, macro calculations, or weight tracking.
- **Immutability Contract:** Historical nutrition snapshots stored on diary entries remain immutable, strictly decoupled from live library or custom recipe edits/deletions.
- **AI Food Recognition:** Modal-based photo capture and gallery picker using `expo-image-picker`. Communicates exclusively with the local Python FastAPI proxy service. Users review, edit portion grams and macros, and provide explicit confirmation before items commit to the SQLite diary.
- **Client Networking:** Resolves `EXPO_PUBLIC_AI_BACKEND_URL` from `.env.local` for physical Android LAN testing, falling back to Android emulator loopback (`10.0.2.2:8000`) or `localhost:8000` for simulator/web. Enforces a 35-second client-side `AbortController` timeout on all recognition calls.

### Backend AI Proxy Architecture (`backend`)
- **Framework:** Python 3.13, FastAPI 0.162.0, Uvicorn 0.54.0.
- **SDK:** Official Google GenAI SDK (`google-genai 2.34.0`).
- **Security Boundary:**
  - `GEMINI_API_KEY` is strictly confined to server-side memory (`backend/.env`, ignored by Git). Never exposed to mobile bundles, exports, or public configuration.
  - Image payloads are validated in-memory using Pillow (`PIL`). All EXIF, GPS, and camera metadata are stripped before sending to the model.
  - Maximum upload size enforced at 10 MiB; strict 20 megapixel limit (`Image.MAX_IMAGE_PIXELS = 20_000_000`) prevents decompression bomb Denial-of-Service attacks.
  - 30-second server request timeout enforced on `types.GenerateContentConfig` via `types.HttpOptions(timeout=30000)`.
  - Structured output validated against Pydantic schema `FoodRecognitionResponse`.

---

## 2. Findings Ranked by Severity

| ID | Severity | Category | Description | Status |
|---|---|---|---|---|
| **SEC-01** | **High** | Tooling Dependencies | Upstream `@expo/cli` / `zod` (3 high) and `@expo/config` / `deepmerge` (5 low) advisories remain unresolved in Expo SDK 58. Source map verified: neither package is bundled into the client runtime. | **Documented / Blocked on Upstream** |
| **SEC-02** | **Medium** | Backend Security | Potential decompression bomb vulnerability if untrusted image files with massive dimensions were uploaded. | **Fixed** (enforced `Image.MAX_IMAGE_PIXELS = 20_000_000` and handled `Image.DecompressionBombError`) |
| **REL-01** | **Medium** | AI Service Reliability | Gemini API SDK call lacked explicit timeout configuration, risking worker hang if Google API stalled. | **Fixed** (configured `http_options=types.HttpOptions(timeout=30000)` and handled timeouts) |
| **REL-02** | **Medium** | Mobile App Lifecycle | Mobile `recognizeFoodFromImage` lacked client-side request timeout, risking indefinite modal hang on unstable mobile connections. | **Fixed** (added 35s `AbortController` timeout and graceful timeout error) |
| **CFG-01** | **Medium** | Android Release Config | `apps/mobile/app.json` was missing `android.package` and `versionCode`, blocking standard Android standalone builds and prebuilds. | **Fixed** (added `"package": "com.bites2go"` and `"versionCode": 1`) |
| **DOC-01** | **Low** | Configuration Clarity | `EXPO_PUBLIC_AI_BACKEND_URL` was undocumented in `.env.example` templates, complicating physical Android device LAN setup. | **Fixed** (documented in `.env.example` and `apps/mobile/.env.example`) |

---

## 3. Fixes Implemented in this Audit

1. **Decompression Bomb Protection (`backend/app/services/image.py`):**
   - Configured `Image.MAX_IMAGE_PIXELS = 20_000_000` (20 megapixels per `docs/SECURITY.md`).
   - Added explicit handling for `Image.DecompressionBombError`, returning a safe `InvalidImageError("Image exceeds maximum allowed resolution (20 megapixels).")`.
   - Added unit test `test_validate_and_sanitize_rejects_decompression_bomb` in `backend/tests/test_image_processing.py`.

2. **Backend Gemini API Request Timeout (`backend/app/services/gemini.py`):**
   - Configured `types.HttpOptions(timeout=timeout_ms)` in `types.GenerateContentConfig` based on `settings.gemini_timeout_seconds` (30s).
   - Added exception handling for `(TimeoutError, httpx.TimeoutException)` mapping to `GeminiServiceError("AI recognition request timed out. Please try again.")`.

3. **Client-Side Network Timeout (`apps/mobile/src/services/aiFoodRecognition.ts`):**
   - Wrapped both base64 and multipart `fetch` calls with an `AbortController` configured for a 35-second timeout.
   - Handled `AbortError` cleanly, surfacing user-facing feedback ("AI recognition request timed out. Please check your connection and try again.").
   - Added unit test in `apps/mobile/tests/aiRecognition.test.mjs` verifying timeout and abort handling.

4. **Android Package Identity (`apps/mobile/app.json`):**
   - Added `"package": "com.bites2go"` and `"versionCode": 1` to `android` config, satisfying EAS Build and native APK release prerequisites.

5. **LAN Configuration Documentation (`.env.example` & `apps/mobile/.env.example`):**
   - Documented `EXPO_PUBLIC_AI_BACKEND_URL` options for physical Android LAN devices (`http://<LAN_IP>:8000`), Android Emulator (`http://10.0.2.2:8000`), and iOS/web (`http://localhost:8000`).

---

## 4. Verification & Test Execution Results

| Check | Scope | Tool / Command | Exit Code | Outcome |
|---|---|---|:---:|---|
| **Mobile Tests** | `apps/mobile` | `node --experimental-strip-types --test tests/*.test.mjs` | 0 | **110 passed, 0 failed, 0 skipped** (~4.18s) |
| **Mobile TypeScript** | `apps/mobile` | `tsc --noEmit` | 0 | **0 errors** |
| **Mobile Linter** | `apps/mobile` | `eslint .` | 0 | **0 errors, 0 warnings** |
| **Mobile Formatter** | `apps/mobile` | `prettier --check .` | 0 | **100% Prettier compliant** |
| **Expo Doctor** | `apps/mobile` | `expo-doctor` | 0 | **20/20 checks passed** |
| **Expo Public Config** | `apps/mobile` | `npx expo config --type public` | 0 | Clean schema with `android.package: "com.bites2go"` |
| **Android Export Bundle**| `apps/mobile` | `npx expo export --platform android` | 0 | **3.1MB Hermes bundle (1,364 modules)** generated in 10.2s |
| **Backend Tests** | `backend` | `pytest backend/tests` | 0 | **15 passed in 0.26s** |
| **Backend Compilation** | `backend` | `python -m py_compile` | 0 | All modules compiled cleanly |
| **Security Scan** | Workspace + Export | `python scripts/security-scan.py --artifact <TEMP_DIR>` | 0 | **574 files/blobs scanned, 0 pattern findings** |
| **Dependency Audit** | `apps/mobile` | `npm audit` | 1 | 8 known upstream advisories (3 high / 5 low in Expo CLI tooling; runtime bundle verified clean) |

---

## 5. Remaining Production Release Blockers

1. **Upstream Expo CLI Tooling Advisories (3 High / 5 Low):**
   - Documented in `docs/RELEASE_READINESS.md`. While source inspection and source maps confirm `zod` and `deepmerge` are excluded from the exported Hermes Android client bundle, official release certification requires upstream Expo SDK patches.
2. **Physical Device Signed Release Testing:**
   - Testing has been confirmed by the user via Expo Go on an Android phone. A formal production release requires building a signed standalone APK/AAB (`eas build -p android`) and verifying native launch, splash transition, TalkBack screen reader accessibility, and offline recovery on low-end hardware without the Expo Go client.
3. **Cloud Synchronization Phase:**
   - Supabase cloud synchronization and authentication remain intentionally disabled per project specifications.

---

## 6. Manual Android Physical Device Verification Steps

To verify Bites2Go on an Android physical phone:

1. **Start Backend Service:**
   ```powershell
   # In terminal 1 (repository root):
   backend\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000
   ```
2. **Determine Host Machine LAN IP:**
   ```powershell
   ipconfig
   # Note IPv4 Address (e.g. 192.168.1.150)
   ```
3. **Configure Mobile Client for LAN Testing:**
   In `apps/mobile/.env.local`:
   ```env
   EXPO_PUBLIC_AI_BACKEND_URL=http://<YOUR_LAN_IP>:8000
   ```
4. **Launch Expo Development Server:**
   ```powershell
   # In terminal 2:
   cd apps/mobile
   npm start
   ```
5. **On Android Phone (Connected to the Same Wi-Fi Network):**
   - Open **Expo Go**.
   - Scan the terminal QR code.
   - Navigate to **Food Search** -> tap **Scan Meal with Gemini AI**.
   - Capture a food photo or choose from gallery.
   - Verify:
     - Image preview renders right-side up.
     - Loading spinner displays while analyzing.
     - Food items, grams, and macros populate with editable fields.
     - Portion gram edits proportionally adjust calories, protein, carbs, and fat.
     - Tapping **Log Items to <Meal>** commits all items atomically to local SQLite diary without "Invalid nutrition snapshot" errors.
     - Restarting the app retains the logged foods in the Diary tab.
