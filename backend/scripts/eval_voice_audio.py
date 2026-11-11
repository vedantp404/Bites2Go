"""Opt-in human audio evaluation runner for POST /api/v1/parse-voice-audio.

Never invoked by pytest or CI. Requires explicit --consent-upload acknowledgment
before reading tester-supplied local recordings and uploading them to the backend.
"""

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any

import httpx


def _match_expected_item(expected_name: str, items: list[dict[str, Any]]) -> dict[str, Any] | None:
    target = expected_name.strip().lower()
    for item in items:
        desc = str(item.get("food_description") or "").strip().lower()
        if target in desc or desc in target:
            return item
    return None


def evaluate_manifest(
    manifest_path: Path,
    base_url: str,
    timeout_seconds: float = 45.0,
) -> dict[str, Any]:
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("Manifest JSON must be a non-empty list of recording test cases.")

    latencies: list[float] = []
    failed_requests = 0
    total_expected_foods = 0
    matched_foods = 0
    total_expected_quantities = 0
    matched_quantities = 0
    total_corrections = 0
    matched_corrections = 0
    per_case: list[dict[str, Any]] = []

    endpoint = f"{base_url.rstrip('/')}/api/v1/parse-voice-audio"

    with httpx.Client(timeout=timeout_seconds) as client:
        for idx, case in enumerate(entries, start=1):
            case_id = str(case.get("id") or f"case-{idx}")
            audio_path = Path(str(case["file"]))
            if not audio_path.is_file():
                failed_requests += 1
                per_case.append({"id": case_id, "ok": False, "error": f"File not found: {audio_path}"})
                continue

            suffix = audio_path.suffix.lower() or ".m4a"
            mime = {
                ".m4a": "audio/m4a",
                ".mp4": "audio/mp4",
                ".aac": "audio/aac",
                ".wav": "audio/wav",
                ".mp3": "audio/mpeg",
                ".ogg": "audio/ogg",
                ".webm": "audio/webm",
                ".flac": "audio/flac",
            }.get(suffix, "audio/m4a")

            data_fields: dict[str, str] = {}
            if case.get("meal_context"):
                data_fields["meal_context"] = str(case["meal_context"])

            t0 = time.perf_counter()
            try:
                with audio_path.open("rb") as fh:
                    resp = client.post(
                        endpoint,
                        files={"file": (audio_path.name, fh, mime)},
                        data=data_fields,
                    )
                elapsed = time.perf_counter() - t0
                latencies.append(elapsed)
            except Exception as exc:
                elapsed = time.perf_counter() - t0
                latencies.append(elapsed)
                failed_requests += 1
                per_case.append({"id": case_id, "ok": False, "latency_s": round(elapsed, 3), "error": type(exc).__name__})
                continue

            if resp.status_code != 200:
                failed_requests += 1
                per_case.append({
                    "id": case_id,
                    "ok": False,
                    "status_code": resp.status_code,
                    "latency_s": round(elapsed, 3),
                })
                continue

            body = resp.json()
            items: list[dict[str, Any]] = body.get("items") or []

            exp_foods: list[str] = [str(x) for x in (case.get("expected_foods") or [])]
            exp_qtys: dict[str, float] = {
                str(k): float(v) for k, v in (case.get("expected_quantities") or {}).items()
            }
            case_food_hits = 0
            for ef in exp_foods:
                total_expected_foods += 1
                if _match_expected_item(ef, items) is not None:
                    matched_foods += 1
                    case_food_hits += 1

            case_qty_hits = 0
            for q_name, q_val in exp_qtys.items():
                total_expected_quantities += 1
                matched_item = _match_expected_item(q_name, items)
                if matched_item is not None:
                    got_qty = float(matched_item.get("quantity") or 0.0)
                    if abs(got_qty - q_val) <= 0.15:
                        matched_quantities += 1
                        case_qty_hits += 1

            corr_expected = bool(case.get("correction_expected"))
            corr_ok = None
            if corr_expected:
                total_corrections += 1
                all_corr_qty_ok = (case_qty_hits == len(exp_qtys)) and (case_food_hits == len(exp_foods))
                corr_ok = all_corr_qty_ok
                if corr_ok:
                    matched_corrections += 1

            per_case.append(
                {
                    "id": case_id,
                    "ok": True,
                    "latency_s": round(elapsed, 3),
                    "items_returned": len(items),
                    "food_hits": f"{case_food_hits}/{len(exp_foods)}",
                    "quantity_hits": f"{case_qty_hits}/{len(exp_qtys)}",
                    "correction_ok": corr_ok,
                }
            )

    total_cases = len(entries)
    return {
        "total_cases": total_cases,
        "unsuccessful_requests": failed_requests,
        "unsuccessful_rate": round(failed_requests / total_cases, 4) if total_cases else 0.0,
        "food_name_accuracy": round(matched_foods / total_expected_foods, 4) if total_expected_foods else None,
        "quantity_accuracy": round(matched_quantities / total_expected_quantities, 4) if total_expected_quantities else None,
        "correction_accuracy": round(matched_corrections / total_corrections, 4) if total_corrections else None,
        "latency_median_s": round(statistics.median(latencies), 3) if latencies else None,
        "latency_max_s": round(max(latencies), 3) if latencies else None,
        "cases": per_case,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Opt-in Bites2Go audio voice evaluation CLI")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to local private evaluation manifest JSON")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument(
        "--consent-upload",
        action="store_true",
        help="Explicitly confirm consent to upload listed local audio files to --url",
    )
    args = parser.parse_args()

    if not args.consent_upload:
        print(
            "Refusing to upload audio without explicit --consent-upload flag.",
            file=sys.stderr,
        )
        return 2

    summary = evaluate_manifest(args.manifest, args.url)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
