from typing import Literal

from pydantic import BaseModel, Field


CharacterPreset = Literal["dense", "minimal", "alphanumeric"]
ColorMode = Literal["grayscale", "color"]


class ConvertOptions(BaseModel):
    output_width: int = Field(default=120, ge=20, le=300)
    preset: CharacterPreset = "dense"
    color_mode: ColorMode = "grayscale"
    invert: bool = False
    brightness: float = Field(default=1.0, ge=0.5, le=1.5)
    contrast: float = Field(default=1.0, ge=0.5, le=1.5)
    dithering: bool = False


class OutputMetadata(BaseModel):
    original_width: int
    original_height: int
    grid_columns: int
    grid_rows: int
    preset: CharacterPreset
    color_mode: ColorMode


class ConvertResponse(BaseModel):
    metadata: OutputMetadata
    text: str
    svg: str
    png_base64: str
