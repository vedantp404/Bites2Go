"""Temporary single-request verification script for live Gemini API."""

import io
import sys
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from PIL import Image

from app.services.gemini import GeminiService
from app.services.image import validate_and_sanitize_image

def main() -> None:
    # Minimal 120x120 test image representing an apple/tomato
    buf = io.BytesIO()
    img = Image.new("RGB", (120, 120), color=(220, 30, 30))
    img.save(buf, format="JPEG")
    sanitized, mime = validate_and_sanitize_image(buf.getvalue())

    print("Initiating single live verification request...")
    service = GeminiService()
    try:
        result = service.recognize_food(sanitized, mime_type=mime)
        print("LIVE_VERIFICATION_STATUS=SUCCESS")
        print(f"ITEMS_FOUND={len(result.items)}")
        print(f"SUMMARY={result.summary}")
        for item in result.items:
            print(
                f"ITEM: {item.food_name} | {item.estimated_quantity} {item.unit} ({item.estimated_grams}g) | "
                f"{item.calories} kcal | P:{item.protein}g C:{item.carbohydrates}g F:{item.fat}g | "
                f"Confidence: {item.uncertainty.confidence_score} ({item.uncertainty.confidence_level})"
            )
    except Exception as exc:
        print("LIVE_VERIFICATION_STATUS=FAILED")
        print(f"ERROR_TYPE={type(exc).__name__}")
        print(f"ERROR_MESSAGE={str(exc)}")
        if exc.__cause__:
            print(f"UNDERLYING_CAUSE={type(exc.__cause__).__name__}: {str(exc.__cause__)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
