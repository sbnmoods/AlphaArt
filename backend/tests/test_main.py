import base64
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def _build_test_image_bytes() -> bytes:
    image = Image.new("RGB", (8, 8), color=(255, 120, 40))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_convert_returns_text_and_svg() -> None:
    response = client.post(
        "/api/v1/convert",
        data={
            "output_width": "40",
            "preset": "dense",
            "color_mode": "grayscale",
            "invert": "false",
            "brightness": "1.0",
            "contrast": "1.0",
            "dithering": "false",
        },
        files={"image": ("sample.png", _build_test_image_bytes(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["grid_columns"] == 40
    assert "<svg" in payload["svg"]
    assert isinstance(payload["text"], str)
    assert base64.b64decode(payload["png_base64"])[:8] == b"\x89PNG\r\n\x1a\n"
