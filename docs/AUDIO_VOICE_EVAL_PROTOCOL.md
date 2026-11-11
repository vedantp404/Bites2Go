# Opt-In Real-Audio Voice Evaluation Protocol (Milestone 4F)

## Purpose & Consent Gate
All automated unit and integration suites (`pytest backend/tests`, `npm test --prefix apps/mobile`) are 100% mocked and consume **zero** live AI quota.

This protocol defines a manual, opt-in human evaluation pass for testing real Android microphone recordings (`.m4a` / `.wav`) against `POST /api/v1/parse-voice-audio` using recordings that the tester explicitly records and consents to uploading.

- **Consent Requirement:** Audio clips are sent only when the tester explicitly places them in a private local manifest (gitignored / never committed) and passes `--consent-upload` to `backend/scripts/eval_voice_audio.py` or speaks/taps **Stop & Analyze** on device.
- **No Audio Retention:** Keep private audio clips and JSON manifests outside tracked Git directories (e.g., `tmp/audio-eval/`). Both the FastAPI backend (in-memory only) and this eval script never store raw recordings on the server.

## Recommended Benchmark Recording Set (10 Clips Max)
Record in normal room environments across Indian English, Hinglish, Hindi, and noisy conditions:

| Case | Spoken Prompt (Natural Delivery) | Primary Checks |
| --- | --- | --- |
| 1 | *"Two scrambled eggs, a slice of sourdough toast with butter, and black coffee. One banana, actually make that two bananas, and a scoop of whey protein."* | All 5 foods intact; sourdough kept; `with butter` modifier; 2 eggs; banana corrected 1->2; whey uncertainty surfaced |
| 2 | *"One roti, actually make that three rotis, and a bowl of yellow dal tadka."* | Roti corrected to `3`; dal matched cleanly |
| 3 | *"100 grams rice, cooked, not raw, with one katori chole."* | Cooked rice `state="cooked"` (`100g`) |
| 4 | *"Do aloo paratha dahi ke saath, aur ek cup adrak chai bina chini."* | Hinglish counts (`2`, `1`, `1`) and `no sugar` modifier |
| 5 | *"Ek glass doodh aur mutthi bhar badam."* | Hindi numerals/units (`1` glass milk, `handful` almonds) |
| 6 | *"Half an avocado on one slice multigrain bread and two boiled egg whites."* | Fractional counts (`0.5`, `1`, `2`) |
| 7 | *"Some chicken curry."* (vague portion) | Honest uncertainty (`portion_specified=false` / clarifying question) |
| 8 | *"Two masala dosa with sambar and coconut chutney"* (background kitchen noise) | Noise resilience without hallucinating extra foods |
| 9 | 0.5–1s silence or non-food ambient audio | Empty `items=[]` / `success=false` without hallucinated meals |
| 10 | Quick double-tap **Stop & Analyze** -> **Confirm & Log to Diary** on device | Zero duplicate SQLite entries; temp audio deleted |

## Metrics Measured Separately
`backend/scripts/eval_voice_audio.py` evaluates and reports five distinct metrics:
1. **Food-Name Recognition Recall:** Fraction of expected canonical dishes/aliases matched in predicted `items`.
2. **Quantity Accuracy:** Fraction of expected items where final numeric quantity (or unit+count) matches within tolerance.
3. **Correction Accuracy:** On clips flagged `"correction_expected": true`, whether ONLY the final corrected value is emitted without retaining retracted counts.
4. **Latency (`s`):** End-to-end HTTP upload + audio inference duration per clip plus median/max.
5. **Unsuccessful Request Rate:** HTTP non-200 or invalid/empty unexpected failures divided by total uploaded clips.

## Running the Opt-In CLI Evaluator
1. Prepare a local (uncommitted) `manifest.json`:
```json
[
  {
    "id": "case-1-breakfast",
    "file": "C:/path/to/private_eval/breakfast_sourdough_correction.m4a",
    "meal_context": "Breakfast",
    "expected_foods": ["scrambled eggs", "sourdough toast", "black coffee", "banana", "whey protein"],
    "expected_quantities": {"scrambled eggs": 2.0, "sourdough toast": 1.0, "black coffee": 1.0, "banana": 2.0, "whey protein": 1.0},
    "correction_expected": true
  }
]
```
2. Run against a local FastAPI server or explicit target URL with `--consent-upload`:
```powershell
backend\.venv\Scripts\python.exe backend\scripts\eval_voice_audio.py `
  --manifest tmp/audio-eval/manifest.json `
  --url http://127.0.0.1:8000 `
  --consent-upload
```
