# api/ocr_api.py
"""
Spiral Codex OCR API - Image text extraction via Tesseract
Accepts uploaded image files or public image URLs and returns extracted text.
"""
import io
import ipaddress
import socket
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, HttpUrl

try:
    from PIL import Image
    import pytesseract

    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False

router = APIRouter(prefix="/v1/ocr", tags=["ocr"])

_ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/tiff",
    "image/bmp",
    "image/gif",
    "image/webp",
}
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_MAX_REDIRECTS = 3


async def _fetch_with_ssrf_protection(url: str) -> bytes:
    """
    Fetch an image from `url` with full SSRF protection:
    - Each redirect hop is validated before being followed.
    - Private/loopback/reserved IP ranges are blocked at every hop.
    Returns the raw response body on success.
    """
    current_url = url
    for hop in range(_MAX_REDIRECTS + 1):
        _validate_url(current_url)
        async with httpx.AsyncClient(follow_redirects=False, timeout=15.0) as client:
            try:
                response = await client.get(current_url)
            except Exception as exc:
                raise HTTPException(
                    status_code=502, detail=f"Failed to fetch image URL: {exc}"
                ) from exc

        if response.is_redirect:
            if hop == _MAX_REDIRECTS:
                raise HTTPException(
                    status_code=502,
                    detail=f"Too many redirects fetching image URL (max {_MAX_REDIRECTS}).",
                )
            location = response.headers.get("location", "")
            if not location:
                raise HTTPException(
                    status_code=502, detail="Redirect response missing Location header."
                )
            # Resolve relative redirects to absolute
            if location.startswith("/"):
                parsed = urlparse(current_url)
                location = f"{parsed.scheme}://{parsed.netloc}{location}"
            current_url = location
        else:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to fetch image URL (HTTP {exc.response.status_code}).",
                ) from exc
            return response.content

    raise HTTPException(  # pragma: no cover
        status_code=502,
        detail=f"Too many redirects fetching image URL (max {_MAX_REDIRECTS}).",
    )
    if not _OCR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="OCR dependencies (Pillow, pytesseract) are not installed.",
        )


def _validate_url(url: str) -> None:
    """Reject URLs that resolve to private/internal network addresses (SSRF guard)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=422, detail="Only http and https URLs are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=422, detail="Invalid URL: missing hostname.")

    try:
        resolved_ip = socket.getaddrinfo(hostname, None)[0][4][0]
    except socket.gaierror as exc:
        raise HTTPException(status_code=422, detail=f"Cannot resolve hostname: {exc}") from exc

    try:
        addr = ipaddress.ip_address(resolved_ip)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid IP address: {exc}") from exc

    if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
        raise HTTPException(
            status_code=422,
            detail="Requests to private or internal network addresses are not allowed.",
        )


def _run_ocr(image_bytes: bytes, lang: Optional[str] = None) -> Dict[str, Any]:
    """Open image bytes and run Tesseract OCR, returning structured results."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Cannot decode image: {exc}") from exc

    kwargs: Dict[str, Any] = {}
    if lang:
        kwargs["lang"] = lang

    try:
        text: str = pytesseract.image_to_string(image, **kwargs)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, **kwargs)
    except pytesseract.pytesseract.TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Tesseract OCR engine not found. Please install tesseract-ocr.",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {exc}") from exc

    # Collect word-level confidences (filter out empty words)
    words = []
    for w, c in zip(data["text"], data["conf"]):
        confidence = int(c)
        if w.strip() and confidence >= 0:
            words.append({"word": w, "confidence": confidence})

    avg_confidence = (
        round(sum(w["confidence"] for w in words) / len(words), 2) if words else 0.0
    )

    return {
        "text": text.strip(),
        "word_count": len(words),
        "avg_confidence": avg_confidence,
        "words": words,
        "image_size": {"width": image.width, "height": image.height},
        "mode": image.mode,
    }


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class OCRUrlRequest(BaseModel):
    url: HttpUrl
    lang: Optional[str] = None


class OCRResponse(BaseModel):
    text: str
    word_count: int
    avg_confidence: float
    words: list
    image_size: Dict[str, int]
    mode: str
    source: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/health")
def ocr_health() -> Dict[str, Any]:
    """OCR subsystem health check."""
    tesseract_version: Optional[str] = None
    if _OCR_AVAILABLE:
        try:
            tesseract_version = str(pytesseract.get_tesseract_version())
        except Exception:
            tesseract_version = "unknown"

    return {
        "ok": _OCR_AVAILABLE,
        "service": "ocr",
        "dependencies": {
            "pillow": _OCR_AVAILABLE,
            "pytesseract": _OCR_AVAILABLE,
            "tesseract_version": tesseract_version,
        },
        "glyph": "⊚",
    }


@router.post("/extract", response_model=OCRResponse)
async def extract_from_upload(
    file: UploadFile = File(..., description="Image file to extract text from"),
    lang: Optional[str] = None,
) -> OCRResponse:
    """
    Extract text from an uploaded image file using Tesseract OCR.

    - **file**: PNG, JPEG, TIFF, BMP, GIF, or WebP image (max 10 MB).
    - **lang**: Optional Tesseract language code (e.g. `eng`, `fra`). Defaults to Tesseract's default.
    """
    _check_availability()

    content_type = file.content_type or ""
    if content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{content_type}'. Allowed: {sorted(_ALLOWED_MIME_TYPES)}",
        )

    image_bytes = await file.read()
    if len(image_bytes) > _MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(image_bytes)} bytes). Maximum allowed: {_MAX_BYTES} bytes.",
        )

    result = _run_ocr(image_bytes, lang=lang)
    return OCRResponse(**result, source=file.filename or "upload")


@router.post("/extract-url", response_model=OCRResponse)
async def extract_from_url(req: OCRUrlRequest) -> OCRResponse:
    """
    Extract text from a publicly accessible image URL using Tesseract OCR.

    - **url**: Publicly reachable image URL (private/internal addresses are blocked).
    - **lang**: Optional Tesseract language code (e.g. `eng`, `fra`).
    """
    _check_availability()

    url_str = str(req.url)
    _validate_url(url_str)

    image_bytes = await _fetch_with_ssrf_protection(url_str)

    # Validate content-type from a HEAD-less approach: open with Pillow and trust the bytes.
    # We also perform a quick MIME check via the fetched Content-Type header by re-requesting.
    # Instead, rely on Pillow to reject non-image data during _run_ocr.
    if len(image_bytes) > _MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large ({len(image_bytes)} bytes). Maximum allowed: {_MAX_BYTES} bytes.",
        )

    result = _run_ocr(image_bytes, lang=req.lang)
    return OCRResponse(**result, source=url_str)
