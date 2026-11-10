# Bites2Go AI Food Recognition Backend

Secure, local FastAPI microservice for AI-powered meal recognition and voice food parsing, featuring task-specific dual-provider routing across Google Gemini and OpenRouter free-tier models.

---

## Task-Specific Dual-Provider Architecture & Failover

```
[Untrusted Expo Mobile App]
       │
       ├──► POST /api/v1/recognize-food (or /base64)
       │      │  - In-memory Pillow validation: EXIF/GPS stripped, downscaled <=1024px @ q82
       │      │  - Server deadline: 35.0s (completes before mobile 45.0s timeout)
       │      ▼
       │    [Photo Primary: Google Gemini Vision (gemini-3.5-flash, thinking_budget=0)]
       │      ├─► Success (~3.6s–8.5s): Returns FoodRecognitionResponse
       │      └─► Quota/429/503/Timeout ─► [Fallback: nvidia/nemotron-3.5-super-vl:free]
       │                                      (Single optional alternative: dots-studio/dots-3-note-preview:free)
       │                                      * Text-only models are strictly rejected before HTTP send *
       │
       └──► POST /api/v1/parse-voice-meal (Text transcripts; Indian + Hinglish + raw/cooked)
              │  - Server deadline: 32.0s (leaves 8s margin before mobile 40.0s timeout)
              │  - Enforceable wall-clock timeout (14.0s) + socket cancellation abort watchdog
              ▼
            [Voice Primary: NVIDIA Nemotron 3 Ultra Free (nvidia/nemotron-3-ultra-550b-a55b:free)]
              ├─► Success (~5s–9.2s): Returns compact VoiceMealParseResponse (max 900 tokens)
              └─► Error/429/Timeout (>14s) ─► [Fallback: Google Gemini Text (gemini-3.5-flash, tb=0)]
```

### Core Architecture Guarantees
1. **Zero Client Leakage:** API keys (`GEMINI_API_KEY`, `OPENROUTER_API_KEY`) remain exclusively on the server. The mobile client never receives or stores third-party API credentials.
2. **Task-Specific Routing & Vision Safety:**
   - Voice meal parsing uses `nvidia/nemotron-3-ultra-550b-a55b:free` as primary to preserve Gemini daily RPD quota for food photos, with `gemini-3.5-flash` (`thinking_budget=0`) as fast fallback.
   - Photo recognition uses `gemini-3.5-flash` (`thinking_budget=0`, AFC disabled) as primary with verified vision-capable OpenRouter fallback (`nvidia/nemotron-3.5-super-vl:free`). Text-only models are explicitly blocked from receiving image payloads (`error_category="model_vision_unsupported"`).
3. **Intelligent Failover:**
   - Daily quota exhaustion (`per day`) triggers immediate failover without wasting retries; transient burst RPM limits (`per minute`) or 503/504 errors fail over within bounded retry/budget rules.
   - Authentication errors (HTTP 401/403) and malformed client payloads (HTTP 400) fail fast without retry loops.
4. **Response Normalization & Review-First Workflow:** Both providers normalize into identical Pydantic schemas (`FoodRecognitionResponse`, `VoiceMealParseResponse`). Results are estimates only, never auto-written to SQLite; users review and edit before saving.
5. **Offline Independence:** If the backend is unreachable or disabled, local offline SQLite logging and manual catalogue search continue uninterrupted.

---

## Configuration & Environment Variables

Copy `backend/.env.example` to `backend/.env`:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` to configure your providers:

```env
# ---------------------------------------------------------------------------
# Provider Architecture Selection (Task-Specific Routing)
# ---------------------------------------------------------------------------
AI_PRIMARY_PROVIDER=gemini
PHOTO_PRIMARY_PROVIDER=gemini
PHOTO_FALLBACK_PROVIDER=openrouter
VOICE_PRIMARY_PROVIDER=openrouter
VOICE_FALLBACK_PROVIDER=gemini
AI_FALLBACK_ENABLED=true

# ---------------------------------------------------------------------------
# Google Gemini (Photo Primary / Voice Fallback)
# ---------------------------------------------------------------------------
# Obtain your free API key at: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
GEMINI_THINKING_BUDGET=0
GEMINI_MAX_OUTPUT_TOKENS=1500
GEMINI_TIMEOUT_SECONDS=14.0
GEMINI_MAX_RETRIES=2

# ---------------------------------------------------------------------------
# OpenRouter (Voice Primary / Photo Vision Fallback)
# ---------------------------------------------------------------------------
# Obtain an OpenRouter key at: https://openrouter.ai/settings/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

VOICE_OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
VOICE_OPENROUTER_ALTERNATIVE_MODEL=
VOICE_PRIMARY_TIMEOUT_SECONDS=14.0
VOICE_OPENROUTER_MAX_TOKENS=900

PHOTO_OPENROUTER_MODEL=nvidia/nemotron-3.5-super-vl:free
PHOTO_OPENROUTER_ALTERNATIVE_MODEL=dots-studio/dots-3-note-preview:free

OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_TIMEOUT_SECONDS=19.0
OPENROUTER_MAX_TOKENS=2000
OPENROUTER_MAX_RETRIES=1

# ---------------------------------------------------------------------------
# Server Runtime Settings, Image Optimization & Request Deadlines
# ---------------------------------------------------------------------------
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
MAX_IMAGE_DIMENSION=1024
IMAGE_JPEG_QUALITY=82
SERVER_DEADLINE_SECONDS=35.0
VOICE_SERVER_DEADLINE_SECONDS=32.0
MAX_IMAGE_SIZE_BYTES=10485760
ALLOWED_ORIGINS=*
```

---

## How to Obtain Keys

### 1. Google Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** and create a key in your project.
4. Set `GEMINI_API_KEY` in `backend/.env`.

### 2. OpenRouter API Key
1. Visit [OpenRouter](https://openrouter.ai/).
2. Create an account or sign in.
3. Navigate to **Keys** (`https://openrouter.ai/settings/keys`).
4. Click **Create Key**, give it a name (e.g., `Bites2Go-Dev`), and copy the key.
5. Set `OPENROUTER_API_KEY` in `backend/.env`.

---

## Disabling Fallback or Overriding Task Providers

To disable automatic failover across both endpoints:
```env
AI_FALLBACK_ENABLED=false
```
To override voice or photo primary providers independently:
```env
VOICE_PRIMARY_PROVIDER=gemini
PHOTO_PRIMARY_PROVIDER=openrouter
```

---

## Known Free-Tier Limitations

1. **Google Gemini Free Tier:**
   - Standard Gemini Flash models on the free tier feature daily request caps (e.g., 20 RPD / shared project quota). Daily quotas reset at midnight Pacific Time.
   - Routing voice transcripts to Nemotron on OpenRouter by default preserves Gemini daily quota for photo vision requests.
   - Setting `GEMINI_THINKING_BUDGET=0` disables default reasoning tokens on `gemini-3.5-flash`, reducing photo latency from ~17.5s to ~3.5s–8.5s. Note: `gemini-3.5-flash-lite` rejects `thinking_budget`; the provider skips it automatically on `-lite` models.
2. **OpenRouter Free Models (`:free`):**
   - `nvidia/nemotron-3-ultra-550b-a55b:free` is text-only (`response_format` unsupported, omitted automatically) and serves as voice primary with compact JSON schema (`VOICE_OPENROUTER_MAX_TOKENS=900`), typically completing in 5s–9.2s (or safely aborting via wall-clock socket teardown at `VOICE_PRIMARY_TIMEOUT_SECONDS=14.0` to reach Gemini fallback inside `VOICE_SERVER_DEADLINE_SECONDS=32.0`).
   - `nvidia/nemotron-3.5-super-vl:free` (plus single alternative `dots-studio/dots-3-note-preview:free`) provides vision-capable fallback for photos.
   - Strict upstream rate limits or empty responses may still occur under heavy free-tier load; genuine failures surface safe retryable errors without hallucinated results.

---

## Running the Server

### 1. Install Python Dependencies
```bash
# Activate virtual environment
# Windows PowerShell:
.\backend\.venv\Scripts\Activate.ps1

# Linux / macOS:
source backend/.venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt
```

### 2. Start the FastAPI Service
From the repository root:
```bash
backend\.venv\Scripts\uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

---

## Verifying the Service

### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```
Example response:
```json
{
  "status": "ok",
  "service": "Bites2Go AI Service",
  "version": "1.0.0",
  "environment": "development",
  "ai_configured": true,
  "primary_provider": "gemini",
  "fallback_enabled": true,
  "gemini_configured": true,
  "openrouter_configured": true,
  "model": "gemini-3.5-flash",
  "fallback_model": "nvidia/nemotron-3.5-super-vl:free",
  "fallback_alternative_model": "dots-studio/dots-3-note-preview:free",
  "photo_primary_provider": "gemini",
  "photo_fallback_provider": "openrouter",
  "photo_model": "gemini-3.5-flash",
  "photo_fallback_model": "nvidia/nemotron-3.5-super-vl:free",
  "voice_primary_provider": "openrouter",
  "voice_fallback_provider": "gemini",
  "voice_model": "nvidia/nemotron-3-ultra-550b-a55b:free",
  "voice_fallback_model": "gemini-3.5-flash",
  "commit": "dev"
}
```

### 2. Run Automated Tests (Mocked - Zero Quota Consumed)
All tests run with mocked HTTP/SDK responses and never hit real APIs or consume API quota:
```bash
# Run all backend tests (115 tests)
PYTHONPATH=backend backend\.venv\Scripts\python.exe -m pytest backend/tests -v

# Run the timeout & task-routing reliability suite specifically
PYTHONPATH=backend backend\.venv\Scripts\python.exe -m pytest backend/tests/test_timeout_reliability.py -v
```

---

## Connecting the Mobile App & APK Compatibility

- **Installed Android APK Compatibility:** All endpoint paths (`/api/v1/recognize-food`, `/api/v1/recognize-food/base64`, `/api/v1/parse-voice-meal`, `/health`) and Pydantic response schemas remain unchanged. Installed APKs work seamlessly without rebuilding once the updated backend is deployed.
- **Timeout Margin Alignment:** Mobile uses `45000ms` (photo) and `40000ms` (voice). Backend enforces `35.0s` (photo) and `32.0s` (voice) server deadlines, leaving `8.0s–10.0s` transport margin so timeouts or fallbacks complete cleanly instead of triggering raw client aborts or HTTP 504s.
- **Render Environment Note:** When deploying to Render, unset legacy `OPENROUTER_MODEL=openrouter/free` (or update `PHOTO_OPENROUTER_MODEL=nvidia/nemotron-3.5-super-vl:free` and `VOICE_OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free`).

1. **Android Emulator:**
   - Maps host `127.0.0.1` to `http://10.0.2.2:8000` automatically.
2. **Physical Device / Local LAN:**
   - In `apps/mobile/.env.local`, set:
     ```env
     EXPO_PUBLIC_AI_BACKEND_URL=http://<YOUR_LOCAL_IP>:8000
     ```
3. **Usage:**
   - Tap **Scan Meal with Gemini AI** on any meal in Bites2Go to take or select a photo.
   - Tap **Voice Log** to enter/review spoken meal descriptions.
   - Detected foods appear in editable cards showing estimated portions and macronutrients.
   - Review and adjust items, then tap **Log to Diary** to save to SQLite.
