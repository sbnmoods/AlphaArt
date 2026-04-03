import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import UnidentifiedImageError
from pydantic import ValidationError

from app.schemas import ConvertOptions, ConvertResponse
from app.services.converter import convert_image_to_character_art


def get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("ALLOWED_ORIGINS")
    if configured_origins:
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    return ["http://localhost:3000", "http://127.0.0.1:3000"]


app = FastAPI(title="AlphaArt API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/convert", response_model=ConvertResponse)
async def convert_image(
    image: UploadFile = File(...),
    output_width: int = Form(120),
    preset: str = Form("dense"),
    color_mode: str = Form("grayscale"),
    invert: bool = Form(False),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    dithering: bool = Form(False),
) -> ConvertResponse:
    if image.content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image type")

    payload = await image.read()
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit")

    try:
        options = ConvertOptions(
            output_width=output_width,
            preset=preset,
            color_mode=color_mode,
            invert=invert,
            brightness=brightness,
            contrast=contrast,
            dithering=dithering,
        )
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors()) from error

    try:
        result = convert_image_to_character_art(payload, options)
    except UnidentifiedImageError as error:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image") from error

    return ConvertResponse(
        metadata=result.metadata,
        text=result.text,
        svg=result.svg,
        png_base64=result.png_base64,
    )
