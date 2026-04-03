from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path
import sys

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas import ConvertOptions  # noqa: E402
from app.services.converter import convert_image_to_character_art  # noqa: E402


OUTPUT_DIR = ROOT / "docs" / "examples"
CANVAS_SIZE = (640, 640)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    examples = {
        "portrait": build_portrait_image(),
        "cat": build_cat_image(),
        "tree": build_tree_image(),
    }

    options = ConvertOptions(
        output_width=96,
        preset="minimal",
        color_mode="grayscale",
        invert=False,
        brightness=1.0,
        contrast=1.15,
        dithering=False,
    )

    for name, image in examples.items():
        input_path = OUTPUT_DIR / f"{name}-input.png"
        output_path = OUTPUT_DIR / f"{name}-output.png"
        text_path = OUTPUT_DIR / f"{name}-output.txt"

        image.save(input_path, format="PNG")

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        result = convert_image_to_character_art(buffer.getvalue(), options)

        output_path.write_bytes(base64.b64decode(result.png_base64))
        text_path.write_text(result.text, encoding="utf-8")


def build_portrait_image() -> Image.Image:
    image = Image.new("RGB", CANVAS_SIZE, "#f5efe7")
    draw = ImageDraw.Draw(image)

    draw.ellipse((150, 80, 490, 420), fill="#f2c9a6")
    draw.pieslice((180, 65, 465, 280), 180, 360, fill="#2f261f")
    draw.rounded_rectangle((220, 360, 420, 610), radius=50, fill="#5d7a9a")
    draw.rectangle((275, 350, 365, 430), fill="#ecc0a0")
    draw.ellipse((225, 210, 285, 260), fill="white")
    draw.ellipse((355, 210, 415, 260), fill="white")
    draw.ellipse((247, 227, 272, 252), fill="#2b221e")
    draw.ellipse((377, 227, 402, 252), fill="#2b221e")
    draw.line((320, 245, 305, 305, 322, 315), fill="#8f5d48", width=6)
    draw.arc((245, 285, 400, 365), start=10, end=170, fill="#9f5149", width=7)
    draw.arc((215, 160, 295, 225), start=200, end=340, fill="#2f261f", width=7)
    draw.arc((345, 160, 425, 225), start=200, end=340, fill="#2f261f", width=7)

    return image


def build_cat_image() -> Image.Image:
    image = Image.new("RGB", CANVAS_SIZE, "#eef3e8")
    draw = ImageDraw.Draw(image)

    draw.ellipse((130, 140, 510, 520), fill="#d9b37a")
    draw.polygon([(185, 205), (255, 65), (315, 210)], fill="#d9b37a")
    draw.polygon([(325, 210), (385, 65), (455, 205)], fill="#d9b37a")
    draw.polygon([(225, 185), (255, 115), (290, 190)], fill="#f1d0b2")
    draw.polygon([(350, 190), (385, 115), (415, 185)], fill="#f1d0b2")
    draw.ellipse((220, 245, 285, 305), fill="white")
    draw.ellipse((355, 245, 420, 305), fill="white")
    draw.ellipse((246, 265, 270, 289), fill="#1c1713")
    draw.ellipse((381, 265, 405, 289), fill="#1c1713")
    draw.polygon([(320, 305), (290, 350), (350, 350)], fill="#9f5f58")
    draw.arc((245, 330, 395, 410), start=20, end=160, fill="#5f4632", width=6)
    draw.line((170, 330, 285, 345), fill="#5f4632", width=4)
    draw.line((170, 365, 285, 360), fill="#5f4632", width=4)
    draw.line((170, 400, 285, 375), fill="#5f4632", width=4)
    draw.line((355, 345, 470, 330), fill="#5f4632", width=4)
    draw.line((355, 360, 470, 365), fill="#5f4632", width=4)
    draw.line((355, 375, 470, 400), fill="#5f4632", width=4)

    return image


def build_tree_image() -> Image.Image:
    image = Image.new("RGB", CANVAS_SIZE, "#dbeaf7")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 470, 640, 640), fill="#d5c39c")
    draw.rectangle((280, 270, 360, 520), fill="#725339")
    draw.ellipse((120, 80, 520, 360), fill="#5f8f4f")
    draw.ellipse((70, 160, 350, 390), fill="#719f5b")
    draw.ellipse((290, 150, 570, 390), fill="#4d7d3c")
    draw.ellipse((210, 20, 430, 210), fill="#6e9c56")
    draw.line((320, 310, 210, 220), fill="#725339", width=18)
    draw.line((330, 315, 430, 220), fill="#725339", width=18)
    draw.line((310, 380, 190, 320), fill="#725339", width=14)
    draw.line((340, 380, 455, 315), fill="#725339", width=14)

    return image


if __name__ == "__main__":
    main()