"""Food recognition API endpoint."""

import asyncio
import base64
import logging
import threading
import time
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field

from app.config import ConfigurationError, Settings, get_settings
from app.models.food import (
    FoodRecognitionResponse,
    VoiceMealParseRequest,
    VoiceMealParseResponse,
)
from app.services.ai_service import DualProviderService, get_ai_service
from app.services.providers.base import (
    AIAllProvidersFailedError,
    AIAuthenticationError,
    AIRateLimitError,
    AIRequestCancelledError,
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
    GeminiServiceError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    ModelOutputValidationError,
    RateLimitError,
    current_cancellation_check,
    current_request_deadline,
    current_request_id,
)
from app.services.audio import (
    AudioSizeExceededError,
    InvalidAudioError,
    validate_and_sanitize_audio,
)
from app.services.image import (
    ImageSizeExceededError,
    InvalidImageError,
    validate_and_sanitize_image,
)

logger = logging.getLogger("bites2go.food_router")

# Backward compatibility alias
get_gemini_service = get_ai_service
GeminiService = DualProviderService

router = APIRouter(prefix="/api/v1", tags=["Food Recognition"])


class Base64ImagePayload(BaseModel):
    """Optional JSON payload for base64 image submissions."""

    image_base64: str = Field(..., description="Base64-encoded image string")


def _bounded_retry_after_header(raw_seconds: Optional[float], default_seconds: int) -> str:
    """Return safe integer Retry-After string clamped to [2, 60] seconds."""
    if raw_seconds is None or raw_seconds <= 0:
        return str(default_seconds)
    clamped = max(2, min(60, int(round(raw_seconds))))
    return str(clamped)


def _http_exception_for_all_providers_failed(
    exc: AIAllProvidersFailedError,
    service_label: str,
    manual_fallback_hint: str,
) -> HTTPException:
    """Map AIAllProvidersFailedError to HTTP 429 when both hit rate limits, else HTTP 503."""
    p_err = getattr(exc, "primary_error", None)
    f_err = getattr(exc, "fallback_error", None)
    raw_retry_after = getattr(f_err, "retry_after_seconds", None) or getattr(
        p_err, "retry_after_seconds", None
    )
    if isinstance(p_err, AIRateLimitError) and isinstance(f_err, AIRateLimitError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"The {service_label} providers are temporarily rate-limited or reached free-tier caps. "
                f"Please wait briefly or {manual_fallback_hint}."
            ),
            headers={
                "Retry-After": _bounded_retry_after_header(raw_retry_after, default_seconds=10),
                "X-Error-Category": "all_providers_rate_limited",
            },
        )
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            f"The {service_label} is temporarily unavailable. "
            f"All configured providers failed to process the request. Please try again or {manual_fallback_hint}."
        ),
        headers={
            "Retry-After": _bounded_retry_after_header(raw_retry_after, default_seconds=3),
            "X-Error-Category": "all_providers_failed",
        },
    )


def _http_exception_for_rate_limit(exc: BaseException) -> HTTPException:
    """Map single-provider AIRateLimitError/RateLimitError with bounded Retry-After and category."""
    raw_ra = getattr(exc, "retry_after_seconds", None)
    category = getattr(exc, "error_category", None) or "rate_limit"
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=str(exc),
        headers={
            "Retry-After": _bounded_retry_after_header(raw_ra, default_seconds=5),
            "X-Error-Category": str(category),
        },
    )


@router.post(
    "/recognize-food",
    response_model=FoodRecognitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Recognize foods and estimate macronutrients from a photo",
)
async def recognize_food(
    request: Request,
    file: Optional[UploadFile] = File(None),
    gemini_service: GeminiService = Depends(get_gemini_service),
    settings: Settings = Depends(get_settings),
) -> FoodRecognitionResponse:
    """Analyze an uploaded food image in-memory and return validated food components.

    - Strips all EXIF metadata and device tags before analysis.
    - Never persists photos to disk or external storage.
    - Supports bounded retries and failover between primary and secondary providers.
    - Aborts immediately if the client disconnects to prevent wasted AI spend.
    - Enforces hard server deadline budgets and non-blocking monitor cleanup.
    """
    t_endpoint_start = time.perf_counter()
    req_id = request.state.request_id
    req_id_token = current_request_id.set(req_id)
    logger.info("[Timing][%s] Endpoint [recognize_food] started", req_id)

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image file in multipart upload. Use field name 'file'.",
        )

    try:
        raw_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file payload.",
        ) from exc

    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        sanitized_bytes, mime_type = validate_and_sanitize_image(raw_bytes)
    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ImageSizeExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    cancel_event = threading.Event()

    async def _monitor_disconnect() -> None:
        while not cancel_event.is_set():
            try:
                disconnected = await asyncio.wait_for(request.is_disconnected(), timeout=0.5)
                if disconnected:
                    cancel_event.set()
                    break
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass
            await asyncio.sleep(0.2)

    monitor_task = asyncio.create_task(_monitor_disconnect())
    token = current_cancellation_check.set(cancel_event.is_set)
    server_deadline = settings.server_deadline_seconds
    deadline_token = current_request_deadline.set(time.monotonic() + server_deadline)

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                gemini_service.recognize_food,
                sanitized_bytes,
                mime_type=mime_type,
            ),
            timeout=server_deadline,
        )
        total_endpoint_elapsed = time.perf_counter() - t_endpoint_start
        logger.info(
            "[Timing][%s] Endpoint [%s] completed successfully in %.3fs (items: %d)",
            req_id,
            "recognize_food",
            total_endpoint_elapsed,
            len(response.items),
        )
        return response

    except asyncio.TimeoutError as exc:
        cancel_event.set()
        elapsed = time.perf_counter() - t_endpoint_start
        logger.warning(
            "[Timing][%s] Food recognition exceeded server deadline budget of %.1fs (elapsed: %.2fs)",
            req_id,
            server_deadline,
            elapsed,
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI food recognition service exceeded its overall server deadline budget. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        ) from exc
    except AIRequestCancelledError as exc:
        logger.info("[Timing][%s] Food recognition cancelled due to client disconnect: %s", req_id, exc)
        raise HTTPException(
            status_code=499,
            detail="Client disconnected before food recognition completed.",
            headers={"X-Error-Category": "client_disconnected"},
        ) from exc
    except asyncio.CancelledError:
        cancel_event.set()
        logger.info("[Timing][%s] Food recognition request task was cancelled.", req_id)
        raise
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
            headers={"X-Error-Category": "configuration"},
        ) from exc
    except AIAllProvidersFailedError as exc:
        raise _http_exception_for_all_providers_failed(
            exc,
            service_label="AI food recognition service",
            manual_fallback_hint="use manual search",
        ) from exc
    except (AIRateLimitError, RateLimitError) as exc:
        raise _http_exception_for_rate_limit(exc) from exc
    except (AITimeoutError, GeminiTimeoutError) as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI food recognition service timed out after multiple attempts. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        ) from exc
    except (AIUnavailableError, GeminiUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI food recognition service is temporarily overloaded or unavailable. Please try again in a few moments.",
            headers={"Retry-After": "3", "X-Error-Category": "upstream_unavailable"},
        ) from exc
    except ModelOutputValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI model returned an unparseable or malformed nutritional response.",
            headers={"X-Error-Category": "model_output"},
        ) from exc
    except (AIServiceError, GeminiServiceError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI food recognition service encountered an error. Please try again.",
            headers={"X-Error-Category": "upstream_error"},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during food recognition.",
        ) from exc
    finally:
        t_cleanup_start = time.perf_counter()
        current_request_deadline.reset(deadline_token)
        current_cancellation_check.reset(token)
        cancel_event.set()
        monitor_task.cancel()
        try:
            await asyncio.wait_for(monitor_task, timeout=0.05)
        except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
            pass
        t_cleanup_elapsed = time.perf_counter() - t_cleanup_start
        logger.info("[Timing][%s] Cancellation-monitor cleanup took %.4fs", req_id, t_cleanup_elapsed)
        current_request_id.reset(req_id_token)


@router.post(
    "/recognize-food/base64",
    response_model=FoodRecognitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Recognize foods from a base64 encoded image string",
)
async def recognize_food_base64(
    request: Request,
    payload: Base64ImagePayload,
    gemini_service: GeminiService = Depends(get_gemini_service),
    settings: Settings = Depends(get_settings),
) -> FoodRecognitionResponse:
    """Analyze a base64-encoded food image string in-memory."""
    t_endpoint_start = time.perf_counter()
    req_id = request.state.request_id
    req_id_token = current_request_id.set(req_id)
    logger.info("[Timing][%s] Endpoint [recognize_food_base64] started", req_id)

    raw_b64 = payload.image_base64.strip()
    if "," in raw_b64:
        raw_b64 = raw_b64.split(",", 1)[1]

    try:
        raw_bytes = base64.b64decode(raw_b64)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 image data.",
        ) from exc

    try:
        sanitized_bytes, mime_type = validate_and_sanitize_image(raw_bytes)
    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ImageSizeExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    cancel_event = threading.Event()

    async def _monitor_disconnect() -> None:
        while not cancel_event.is_set():
            try:
                disconnected = await asyncio.wait_for(request.is_disconnected(), timeout=0.5)
                if disconnected:
                    cancel_event.set()
                    break
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass
            await asyncio.sleep(0.2)

    monitor_task = asyncio.create_task(_monitor_disconnect())
    token = current_cancellation_check.set(cancel_event.is_set)
    server_deadline = settings.server_deadline_seconds
    deadline_token = current_request_deadline.set(time.monotonic() + server_deadline)

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                gemini_service.recognize_food,
                sanitized_bytes,
                mime_type=mime_type,
            ),
            timeout=server_deadline,
        )
        total_endpoint_elapsed = time.perf_counter() - t_endpoint_start
        logger.info(
            "[Timing][%s] Endpoint [%s] completed successfully in %.3fs (items: %d)",
            req_id,
            "recognize_food_base64",
            total_endpoint_elapsed,
            len(response.items),
        )
        return response

    except asyncio.TimeoutError as exc:
        cancel_event.set()
        elapsed = time.perf_counter() - t_endpoint_start
        logger.warning(
            "[Timing][%s] Food recognition base64 exceeded server deadline budget of %.1fs (elapsed: %.2fs)",
            req_id,
            server_deadline,
            elapsed,
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI food recognition service exceeded its overall server deadline budget. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        ) from exc
    except AIRequestCancelledError as exc:
        logger.info("[Timing][%s] Food recognition base64 cancelled due to client disconnect: %s", req_id, exc)
        raise HTTPException(
            status_code=499,
            detail="Client disconnected before food recognition completed.",
            headers={"X-Error-Category": "client_disconnected"},
        ) from exc
    except asyncio.CancelledError:
        cancel_event.set()
        logger.info("[Timing][%s] Food recognition base64 request task was cancelled.", req_id)
        raise
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
            headers={"X-Error-Category": "configuration"},
        ) from exc
    except AIAllProvidersFailedError as exc:
        raise _http_exception_for_all_providers_failed(
            exc,
            service_label="AI food recognition service",
            manual_fallback_hint="use manual search",
        ) from exc
    except (AIRateLimitError, RateLimitError) as exc:
        raise _http_exception_for_rate_limit(exc) from exc
    except (AITimeoutError, GeminiTimeoutError) as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI food recognition service timed out after multiple attempts. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        ) from exc
    except (AIUnavailableError, GeminiUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI food recognition service is temporarily overloaded or unavailable. Please try again in a few moments.",
            headers={"Retry-After": "3", "X-Error-Category": "upstream_unavailable"},
        ) from exc
    except ModelOutputValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI model returned an unparseable or malformed nutritional response.",
            headers={"X-Error-Category": "model_output"},
        ) from exc
    except (AIServiceError, GeminiServiceError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI food recognition service encountered an error. Please try again.",
            headers={"X-Error-Category": "upstream_error"},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during food recognition.",
        ) from exc
    finally:
        t_cleanup_start = time.perf_counter()
        current_request_deadline.reset(deadline_token)
        current_cancellation_check.reset(token)
        cancel_event.set()
        monitor_task.cancel()
        try:
            await asyncio.wait_for(monitor_task, timeout=0.05)
        except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
            pass
        t_cleanup_elapsed = time.perf_counter() - t_cleanup_start
        logger.info("[Timing][%s] Cancellation-monitor cleanup took %.4fs", req_id, t_cleanup_elapsed)
        current_request_id.reset(req_id_token)


def _http_exception_for_voice_error(
    exc: BaseException,
    req_id: str,
    server_deadline: float,
    elapsed: float,
    endpoint_label: str,
) -> HTTPException:
    """Translate provider/deadline exceptions cleanly for voice endpoints."""
    if isinstance(exc, asyncio.TimeoutError):
        logger.warning(
            "[Timing][%s] %s exceeded server deadline budget of %.1fs (elapsed: %.2fs)",
            req_id,
            endpoint_label,
            server_deadline,
            elapsed,
        )
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI voice service exceeded its processing time limit. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        )
    if isinstance(exc, AIRequestCancelledError):
        logger.info("[Timing][%s] %s cancelled due to client disconnect: %s", req_id, endpoint_label, exc)
        return HTTPException(
            status_code=499,
            detail="Client disconnected before voice analysis completed.",
            headers={"X-Error-Category": "client_disconnected"},
        )
    if isinstance(exc, ConfigurationError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
            headers={"X-Error-Category": "configuration"},
        )
    if isinstance(exc, AIAllProvidersFailedError):
        return _http_exception_for_all_providers_failed(
            exc,
            service_label="AI voice service",
            manual_fallback_hint="edit the transcript or search foods manually",
        )
    if isinstance(exc, (AIRateLimitError, RateLimitError)):
        return _http_exception_for_rate_limit(exc)
    if isinstance(exc, (AITimeoutError, GeminiTimeoutError)):
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI voice service timed out. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        )
    if isinstance(exc, (AIUnavailableError, GeminiUnavailableError)):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI voice service is temporarily overloaded or unavailable. Please try again in a few moments.",
            headers={"Retry-After": "3", "X-Error-Category": "upstream_unavailable"},
        )
    if isinstance(exc, ModelOutputValidationError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI voice service could not structure the spoken meal reliably. Please try again or search manually.",
            headers={"X-Error-Category": "model_output"},
        )
    if isinstance(exc, (AIServiceError, GeminiServiceError)):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI voice service encountered an error. Please try again.",
            headers={"X-Error-Category": "upstream_error"},
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred during voice meal analysis.",
    )


@router.post(
    "/parse-voice-meal",
    response_model=VoiceMealParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse spoken food description into structured items and nutritional estimates",
)
async def parse_voice_meal(
    request: Request,
    payload: VoiceMealParseRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
    settings: Settings = Depends(get_settings),
) -> VoiceMealParseResponse:
    """Analyze a spoken food description transcript and return validated food components.

    - Decomposes multi-item utterances (e.g. '2 rotis and a bowl of dal').
    - Translates colloquial measures (bowls, handfuls, slices) into realistic gram estimates.
    - Resolves in-flight corrections (e.g. 'one roti, actually make that two').
    - Distinguishes raw vs cooked state.
    - Cancels immediately if client disconnects.
    - Enforces hard server deadline budgets and non-blocking monitor cleanup.
    """
    t_endpoint_start = time.perf_counter()
    req_id = request.state.request_id
    req_id_token = current_request_id.set(req_id)
    logger.info("[Timing][%s] Endpoint [parse_voice_meal] started", req_id)

    cleaned_transcript = payload.transcript.strip()
    if not cleaned_transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript cannot be empty or whitespace only.",
        )

    cancel_event = threading.Event()

    async def _monitor_disconnect() -> None:
        while not cancel_event.is_set():
            try:
                disconnected = await asyncio.wait_for(request.is_disconnected(), timeout=0.5)
                if disconnected:
                    cancel_event.set()
                    break
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass
            await asyncio.sleep(0.2)

    monitor_task = asyncio.create_task(_monitor_disconnect())
    token = current_cancellation_check.set(cancel_event.is_set)
    server_deadline = settings.voice_server_deadline_seconds
    deadline_token = current_request_deadline.set(time.monotonic() + server_deadline)

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                gemini_service.parse_voice_meal,
                transcript=cleaned_transcript,
                meal_context=payload.meal_context,
            ),
            timeout=server_deadline,
        )
        total_endpoint_elapsed = time.perf_counter() - t_endpoint_start
        logger.info(
            "[Timing][%s] Endpoint [%s] completed successfully in %.3fs (items: %d)",
            req_id,
            "parse_voice_meal",
            total_endpoint_elapsed,
            len(response.items),
        )
        return response

    except asyncio.TimeoutError as exc:
        cancel_event.set()
        elapsed = time.perf_counter() - t_endpoint_start
        logger.warning(
            "[Timing][%s] Voice meal parsing exceeded server deadline budget of %.1fs (elapsed: %.2fs)",
            req_id,
            server_deadline,
            elapsed,
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI voice parsing service exceeded its overall server deadline budget. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        ) from exc
    except AIRequestCancelledError as exc:
        logger.info("[Timing][%s] Voice meal parsing cancelled due to client disconnect: %s", req_id, exc)
        raise HTTPException(
            status_code=499,
            detail="Client disconnected before voice meal parsing completed.",
            headers={"X-Error-Category": "client_disconnected"},
        ) from exc
    except asyncio.CancelledError:
        cancel_event.set()
        logger.info("[Timing][%s] Voice meal parsing request task was cancelled.", req_id)
        raise
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
            headers={"X-Error-Category": "configuration"},
        ) from exc
    except AIAllProvidersFailedError as exc:
        raise _http_exception_for_all_providers_failed(
            exc,
            service_label="AI voice parsing service",
            manual_fallback_hint="use offline catalogue matching or type your foods manually",
        ) from exc
    except (AIRateLimitError, RateLimitError) as exc:
        raise _http_exception_for_rate_limit(exc) from exc
    except (AITimeoutError, GeminiTimeoutError) as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI voice parsing service timed out after multiple attempts. Please try again.",
            headers={"Retry-After": "2", "X-Error-Category": "upstream_timeout"},
        ) from exc
    except (AIUnavailableError, GeminiUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI voice parsing service is temporarily overloaded or unavailable. Please try again in a few moments.",
            headers={"Retry-After": "3", "X-Error-Category": "upstream_unavailable"},
        ) from exc
    except ModelOutputValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI model returned an unparseable or malformed food parsing response.",
            headers={"X-Error-Category": "model_output"},
        ) from exc
    except (AIServiceError, GeminiServiceError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI voice parsing service encountered an error. Please try again.",
            headers={"X-Error-Category": "upstream_error"},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during voice food parsing.",
        ) from exc
    finally:
        t_cleanup_start = time.perf_counter()
        current_request_deadline.reset(deadline_token)
        current_cancellation_check.reset(token)
        cancel_event.set()
        monitor_task.cancel()
        try:
            await asyncio.wait_for(monitor_task, timeout=0.05)
        except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
            pass
        t_cleanup_elapsed = time.perf_counter() - t_cleanup_start
        logger.info("[Timing][%s] Cancellation-monitor cleanup took %.4fs", req_id, t_cleanup_elapsed)
        current_request_id.reset(req_id_token)


@router.post(
    "/parse-voice-audio",
    response_model=VoiceMealParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Interpret a recorded spoken meal audio file directly with multimodal AI",
)
async def parse_voice_audio(
    request: Request,
    file: Optional[UploadFile] = File(None),
    meal_context: Optional[str] = Form(None),
    logged_date: Optional[str] = Form(None),
    gemini_service: GeminiService = Depends(get_gemini_service),
    settings: Settings = Depends(get_settings),
) -> VoiceMealParseResponse:
    """Analyze an uploaded voice recording strictly in memory and return structured meal items.

    - Audio bytes remain strictly in memory for the duration of this request; never saved to disk or logged.
    - Interprets English, Indian English, Hindi, and Hinglish speech including spoken self-corrections.
    - Aborts immediately if the client disconnects or upload cancels.
    - Enforces bounded server deadline budgets before mobile upload timeout.
    """
    t_endpoint_start = time.perf_counter()
    req_id = request.state.request_id
    req_id_token = current_request_id.set(req_id)
    logger.info("[Timing][%s] Endpoint [parse_voice_audio] started", req_id)

    if file is None:
        current_request_id.reset(req_id_token)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing audio file in multipart upload. Use field name 'file'.",
        )

    try:
        raw_bytes = await file.read()
    except Exception as exc:
        current_request_id.reset(req_id_token)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded audio file payload.",
        ) from exc

    if not raw_bytes:
        current_request_id.reset(req_id_token)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio recording is empty.",
        )

    try:
        sanitized_bytes, canonical_mime = validate_and_sanitize_audio(
            raw_bytes,
            content_type=file.content_type,
            filename=file.filename,
            max_size_bytes=getattr(settings, "max_audio_size_bytes", 10 * 1024 * 1024),
        )
    except InvalidAudioError as exc:
        current_request_id.reset(req_id_token)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except AudioSizeExceededError as exc:
        current_request_id.reset(req_id_token)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc

    cancel_event = threading.Event()

    async def _monitor_disconnect() -> None:
        while not cancel_event.is_set():
            try:
                disconnected = await asyncio.wait_for(request.is_disconnected(), timeout=0.5)
                if disconnected:
                    cancel_event.set()
                    break
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass
            await asyncio.sleep(0.2)

    monitor_task = asyncio.create_task(_monitor_disconnect())
    token = current_cancellation_check.set(cancel_event.is_set)
    server_deadline = getattr(settings, "voice_audio_server_deadline_seconds", 32.0)
    deadline_token = current_request_deadline.set(time.monotonic() + server_deadline)

    cleaned_context = meal_context.strip()[:50] if isinstance(meal_context, str) and meal_context.strip() else None

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                gemini_service.parse_voice_audio,
                audio_bytes=sanitized_bytes,
                mime_type=canonical_mime,
                meal_context=cleaned_context,
            ),
            timeout=server_deadline,
        )
        total_endpoint_elapsed = time.perf_counter() - t_endpoint_start
        logger.info(
            "[Timing][%s] Endpoint [parse_voice_audio] completed in %.3fs (mime=%s, items=%d)",
            req_id,
            total_endpoint_elapsed,
            canonical_mime,
            len(response.items),
        )
        return response
    except asyncio.CancelledError:
        cancel_event.set()
        logger.info("[Timing][%s] Audio voice request task was cancelled.", req_id)
        raise
    except Exception as exc:
        if isinstance(exc, asyncio.TimeoutError):
            cancel_event.set()
        elapsed = time.perf_counter() - t_endpoint_start
        raise _http_exception_for_voice_error(
            exc,
            req_id=req_id,
            server_deadline=server_deadline,
            elapsed=elapsed,
            endpoint_label="Audio voice parsing",
        ) from exc
    finally:
        t_cleanup_start = time.perf_counter()
        current_request_deadline.reset(deadline_token)
        current_cancellation_check.reset(token)
        cancel_event.set()
        monitor_task.cancel()
        try:
            await asyncio.wait_for(monitor_task, timeout=0.05)
        except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
            pass
        t_cleanup_elapsed = time.perf_counter() - t_cleanup_start
        logger.info("[Timing][%s] Cancellation-monitor cleanup took %.4fs", req_id, t_cleanup_elapsed)
        current_request_id.reset(req_id_token)
