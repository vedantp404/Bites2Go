# Bites2Go AI Food Recognition Backend

Secure, local FastAPI microservice for AI-powered meal recognition and nutritional estimation using the official Google GenAI Python SDK (`google-genai`).

---

## Architecture & Security Boundary

```
[Untrusted Expo Mobile App]
       │
       │ (Sends image bytes via POST /api/v1/recognize-food)
       ▼
[Local Bites2Go FastAPI Microservice (Trusted Server Boundary)]
  - Reads GEMINI_API_KEY from backend/.env (Strictly server-side)
  - Memory-only image processing with Pillow (No disk persistence)
  - EXIF metadata & GPS location stripped
  - Dynamic aspect-ratio resizing
  - Pydantic schema validation & macro consistency checks
       │
       │ (Authenticated Gemini Request via official google-genai SDK)
       ▼
[Google AI Studio / Gemini 3.5 Flash]
```

- **Zero Client Leakage:** The `GEMINI_API_KEY` is loaded strictly on the server and is never exposed in Expo public configs, client bundles, or mobile storage.
- **In-Memory Image Processing:** Photos are processed in RAM using `io.BytesIO`. Uploaded photos are never saved to disk or external cloud buckets.
- **Safe Fallback:** The mobile application remains 100% functional offline with manual SQLite food logging if the backend is stopped or unreachable.

---

## Getting Started

### 1. Prerequisites
- Python 3.11+
- Google AI Studio API key

### 2. Environment Setup
The backend loads its configuration from `backend/.env` (which is excluded from Git tracking):
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env` and insert your API key:
```env
GEMINI_API_KEY=your_google_ai_studio_api_key_here
GEMINI_MODEL=gemini-3.5-flash
PORT=8000
```

### 3. Install Dependencies
```bash
# Create and activate virtual environment
python -m venv backend/.venv

# Windows PowerShell:
.\backend\.venv\Scripts\Activate.ps1

# Linux / macOS:
source backend/.venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt
```

### 4. Run the Server
From the project root:
```bash
backend\.venv\Scripts\uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

---

## Verifying the Backend

### Health Check (Safe, No Credentials Echoed)
```bash
curl http://127.0.0.1:8000/health
```
Expected output:
```json
{
  "status": "ok",
  "service": "Bites2Go AI Service",
  "version": "1.0.0",
  "environment": "development",
  "ai_configured": true,
  "model": "gemini-3.5-flash"
}
```

### Run Automated Tests (Mocked - Zero Quota Consumed)
```bash
backend\.venv\Scripts\pytest.exe backend/tests -v
```

### One-Time Live API Verification
To test live connectivity with your configured Google AI Studio key:
```bash
backend\.venv\Scripts\python.exe backend/verify_live.py
```

---

## Connecting the Mobile App

1. **Android Emulator:**
   - Android Emulator maps host loopback `127.0.0.1` to `http://10.0.2.2:8000` automatically.
   - Start the backend on `127.0.0.1:8000` and launch the app in Expo.
2. **Physical Device / Local LAN:**
   - Find your development machine's local IP (e.g. `192.168.1.15`).
   - Start uvicorn binding to `0.0.0.0`:
     ```bash
     uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
     ```
   - In `apps/mobile/.env.local`, set:
     ```env
     EXPO_PUBLIC_AI_BACKEND_URL=http://192.168.1.15:8000
     ```
   - In the mobile app, navigate to **Log Food** on any meal, tap **Scan Meal with Gemini AI**, snap or select a photo, review the editable nutrition candidates, and tap **Log to Diary**.

