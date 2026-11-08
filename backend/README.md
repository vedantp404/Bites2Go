# Bites2Go AI Food Recognition Backend

Secure, local FastAPI microservice for AI-powered meal recognition and voice food parsing, featuring a resilient dual-provider architecture with Google Gemini as primary and OpenRouter as intelligent fallback.

---

## Dual-Provider Architecture & Intelligent Fallback

```
[Untrusted Expo Mobile App]
       │
       │ (Sends image bytes via POST /api/v1/recognize-food or voice transcript via POST /api/v1/parse-voice-meal)
       ▼
[Bites2Go FastAPI Service (Trusted Server Boundary)]
  │ - Strict in-memory processing (Pillow, io.BytesIO, no disk persistence)
  │ - EXIF & GPS metadata stripped, aspect ratio preserved
  │ - API keys stored strictly in backend/.env (Never leaked to mobile app)
  │
  ├──► [Primary Provider: Google Gemini (e.g. gemini-3.5-flash)]
  │      │
  │      ├─► Success: Returns normalized FoodRecognitionResponse
  │      ├─► HTTP 503/504/Timeout: Bounded retries with exponential backoff & jitter
  │      └─► HTTP 429 / Quota Exhaustion / Retries Exhausted: Failover triggered
  │
  └──► [Fallback Provider: OpenRouter (e.g. openrouter/free)]
         │
         ├─► Activated automatically when Gemini quota is exhausted or unavailable
         ├─► Standardized chat completions format with base64 image / structured JSON
         ├─► Bounded retries for transient OpenRouter network errors
         └─► Normalized into identical FoodRecognitionResponse schema
```

### Core Architecture Guarantees
1. **Zero Client Leakage:** API keys (`GEMINI_API_KEY`, `OPENROUTER_API_KEY`) remain exclusively on the server. The mobile client never receives or stores third-party API credentials.
2. **Intelligent Failover:**
   - When Gemini returns HTTP 429 / Quota Exhaustion, the backend stops retrying Gemini immediately and switches to OpenRouter without wasting attempts or quota.
   - For transient server failures (HTTP 503/504), Gemini executes bounded retries before failing over.
   - Authentication errors (HTTP 401) and malformed requests (HTTP 400) fail fast without retry loops.
3. **Response Normalization:** Both providers return the exact same validated Pydantic schemas (`FoodRecognitionResponse`, `VoiceMealParseResponse`).
4. **Safety & Review-First Workflow:** AI responses are nutritional estimates, never authoritative facts. The backend never writes directly to SQLite. The user must review and edit portion weights and dish names before saving to the diary.
5. **Offline Independence:** If the backend is unreachable or disabled, local offline SQLite logging and manual catalogue search continue to function without interruption.

---

## Configuration & Environment Variables

Copy `backend/.env.example` to `backend/.env`:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` to configure your providers:

```env
# ---------------------------------------------------------------------------
# Provider Architecture Selection
# ---------------------------------------------------------------------------
AI_PRIMARY_PROVIDER=gemini
AI_FALLBACK_ENABLED=true

# ---------------------------------------------------------------------------
# Google Gemini (Primary Provider)
# ---------------------------------------------------------------------------
# Obtain your free API key at: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
GEMINI_TIMEOUT_SECONDS=15.0
GEMINI_MAX_RETRIES=1

# ---------------------------------------------------------------------------
# OpenRouter (Fallback Provider)
# ---------------------------------------------------------------------------
# Obtain an OpenRouter key at: https://openrouter.ai/settings/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# OpenRouter Model identifier:
# "openrouter/free" is the official smart router that automatically routes to
# active free multimodal vision models (e.g. Gemma 4, Nemotron Super VL).
# Alternatively specify a fixed model identifier (e.g. google/gemma-4-31b-it:free).
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_TIMEOUT_SECONDS=25.0
OPENROUTER_MAX_RETRIES=1

# ---------------------------------------------------------------------------
# Server Runtime Settings
# ---------------------------------------------------------------------------
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
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

## Disabling Fallback (Gemini-Only Operation)

To disable the OpenRouter backup provider and run solely with Gemini:
```env
AI_FALLBACK_ENABLED=false
```
When fallback is disabled, Gemini rate limit (429) and timeout (504) errors will be returned directly to the mobile app without invoking OpenRouter.

To use OpenRouter as the primary provider:
```env
AI_PRIMARY_PROVIDER=openrouter
```

---

## Known Free-Tier Limitations

1. **Google Gemini Free Tier:**
   - Standard Gemini Flash models on the free tier feature daily request caps (e.g., 20 Requests Per Day for standard flash endpoints). Daily quotas reset at midnight Pacific Time.
   - When the 20 RPD cap is reached, Gemini returns HTTP 429 (`RESOURCE_EXHAUSTED`). Bites2Go's dual-provider architecture catches this and transparently switches to OpenRouter.
2. **OpenRouter Free Tier (`openrouter/free`):**
   - Free models (`:free`) on OpenRouter are subject to provider availability and rotation.
   - Using `openrouter/free` routes to whatever active free vision model is currently operational.
   - Strict rate limits (e.g., 20-50 requests per day) may apply across free models depending on OpenRouter traffic.
   - Adding a small credit balance (e.g., $5) to OpenRouter unlocks high-volume paid models (like `google/gemini-2.5-flash` at fractions of a cent per image) if higher throughput is desired.

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
  "fallback_model": "openrouter/free"
}
```

### 2. Run Automated Tests (Mocked - Zero Quota Consumed)
All tests run with mocked HTTP responses and never hit real APIs or consume API quota:
```bash
# Run all backend tests (56 tests)
backend\.venv\Scripts\pytest.exe backend/tests -v

# Run the dual-provider fallback suite specifically
backend\.venv\Scripts\pytest.exe backend/tests/test_dual_provider.py -v
```

---

## Connecting the Mobile App

1. **Android Emulator:**
   - Maps host `127.0.0.1` to `http://10.0.2.2:8000` automatically.
2. **Physical Device / Local LAN:**
   - In `apps/mobile/.env.local`, set:
     ```env
     EXPO_PUBLIC_AI_BACKEND_URL=http://<YOUR_LOCAL_IP>:8000
     ```
3. **Usage:**
   - Tap **Scan Meal with Gemini AI** on any meal in Bites2Go to take or select a photo.
   - Tap **Voice Log** to record spoken meals.
   - Detected foods appear in editable cards showing estimated portions and macronutrients.
   - Review and adjust items, then tap **Log to Diary** to save to SQLite.
