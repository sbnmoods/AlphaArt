from __future__ import annotations

import base64
from dataclasses import dataclass
from html import escape
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from app.schemas import ConvertOptions, OutputMetadata


CHARACTER_RAMPS = {
    "dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "minimal": "@#:. ",
    "alphanumeric": "@B8RMWNXVYIti+=;:,. ",
}

CELL_ASPECT_RATIO = 0.5
FONT_FAMILY = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
EDGE_BLEND = 0.22
LOCAL_CONTRAST_BLEND = 0.5


@dataclass
class ConversionResult:
    metadata: OutputMetadata
    text: str
    svg: str
    png_base64: str


def convert_image_to_character_art(image_bytes: bytes, options: ConvertOptions) -> ConversionResult:
    image = Image.open(BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image).convert("RGB")

    processed = _apply_adjustments(image, options)
    grid_image = _resize_to_grid(processed, options.output_width)

    grid = np.asarray(grid_image, dtype=np.uint8)
    grayscale = _prepare_grayscale_map(grid, options.invert)

    ramp = CHARACTER_RAMPS[options.preset]
    text_rows = _map_pixels_to_rows(grayscale, ramp)

    metadata = OutputMetadata(
        original_width=image.width,
        original_height=image.height,
        grid_columns=grid_image.width,
        grid_rows=grid_image.height,
        preset=options.preset,
        color_mode=options.color_mode,
    )
    text = "\n".join(text_rows)
    svg = _render_svg(text_rows, grid, options)
    png_base64 = _render_png(text_rows, grid, options)
    return ConversionResult(metadata=metadata, text=text, svg=svg, png_base64=png_base64)


def _apply_adjustments(image: Image.Image, options: ConvertOptions) -> Image.Image:
    adjusted = ImageEnhance.Brightness(image).enhance(options.brightness)
    adjusted = ImageEnhance.Contrast(adjusted).enhance(options.contrast)
    adjusted = ImageOps.autocontrast(adjusted, cutoff=1)
    adjusted = adjusted.filter(ImageFilter.UnsharpMask(radius=1.6, percent=180, threshold=2))
    adjusted = adjusted.filter(ImageFilter.DETAIL)
    if options.dithering:
        adjusted = adjusted.convert("L").convert("1").convert("RGB")
    return adjusted


def _resize_to_grid(image: Image.Image, output_width: int) -> Image.Image:
    width, height = image.size
    output_height = max(1, round((height / width) * output_width * CELL_ASPECT_RATIO))
    return image.resize((output_width, output_height), Image.Resampling.LANCZOS)


def _prepare_grayscale_map(grid: np.ndarray, invert: bool) -> np.ndarray:
    grayscale = np.dot(grid[..., :3], [0.299, 0.587, 0.114]).astype(np.float32)
    local_average = (
        grayscale
        + np.roll(grayscale, 1, axis=0)
        + np.roll(grayscale, -1, axis=0)
        + np.roll(grayscale, 1, axis=1)
        + np.roll(grayscale, -1, axis=1)
    ) / 5.0
    local_contrast = grayscale - local_average

    gradient_y, gradient_x = np.gradient(grayscale)
    edge_strength = np.hypot(gradient_x, gradient_y)
    if edge_strength.max() > 0:
        edge_strength = (edge_strength / edge_strength.max()) * 255.0

    detailed = grayscale + (local_contrast * LOCAL_CONTRAST_BLEND) - (edge_strength * EDGE_BLEND)
    detailed = np.clip(detailed, 0, 255)

    if invert:
        detailed = 255 - detailed

    return detailed


def _map_pixels_to_rows(grayscale: np.ndarray, ramp: str) -> list[str]:
    ramp_length = len(ramp) - 1

    rows: list[str] = []
    for row in grayscale:
        indices = np.rint((row / 255) * ramp_length).astype(int)
        rows.append("".join(ramp[index] for index in indices))
    return rows


def _render_svg(text_rows: list[str], grid: np.ndarray, options: ConvertOptions) -> str:
    font_size = 8
    line_height = 10
    width = max(1, len(text_rows[0])) * font_size
    height = max(1, len(text_rows)) * line_height

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="AlphaArt output">',
        f'<rect width="100%" height="100%" fill="{"black" if options.color_mode == "grayscale" else "#111111"}" />',
    ]

    for row_index, text_row in enumerate(text_rows):
        y = (row_index + 1) * line_height - 2
        if options.color_mode == "color":
            color_spans = []
            for column_index, character in enumerate(text_row):
                red, green, blue = grid[row_index, column_index]
                color_spans.append(
                    f'<tspan x="{column_index * font_size}" y="{y}" fill="rgb({red},{green},{blue})">{escape(character)}</tspan>'
                )
            lines.append(
                f'<text font-family="{FONT_FAMILY}" font-size="{font_size}" xml:space="preserve">{"".join(color_spans)}</text>'
            )
        else:
            lines.append(
                f'<text x="0" y="{y}" fill="white" font-family="{FONT_FAMILY}" font-size="{font_size}" xml:space="preserve">{escape(text_row)}</text>'
            )

    lines.append("</svg>")
    return "".join(lines)


def _render_png(text_rows: list[str], grid: np.ndarray, options: ConvertOptions) -> str:
    font_size = 8
    line_height = 10
    width = max(1, len(text_rows[0])) * font_size
    height = max(1, len(text_rows)) * line_height
    background = (0, 0, 0) if options.color_mode == "grayscale" else (17, 17, 17)
    foreground = (255, 255, 255)

    image = Image.new("RGB", (width, height), color=background)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for row_index, text_row in enumerate(text_rows):
        y = row_index * line_height
        if options.color_mode == "color":
            for column_index, character in enumerate(text_row):
                red, green, blue = grid[row_index, column_index]
                draw.text(
                    (column_index * font_size, y),
                    character,
                    fill=(int(red), int(green), int(blue)),
                    font=font,
                )
        else:
            draw.text((0, y), text_row, fill=foreground, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")
