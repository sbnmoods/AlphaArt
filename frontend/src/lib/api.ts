export type ConvertRequest = {
  image: File;
  outputWidth: number;
  preset: "dense" | "minimal" | "alphanumeric";
  colorMode: "grayscale" | "color";
  invert: boolean;
  brightness: number;
  contrast: number;
  dithering: boolean;
};

export type ConvertResponse = {
  metadata: {
    original_width: number;
    original_height: number;
    grid_columns: number;
    grid_rows: number;
    preset: string;
    color_mode: string;
  };
  text: string;
  svg: string;
  png_base64: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function convertImage(request: ConvertRequest): Promise<ConvertResponse> {
  const formData = new FormData();
  formData.append("image", request.image);
  formData.append("output_width", String(request.outputWidth));
  formData.append("preset", request.preset);
  formData.append("color_mode", request.colorMode);
  formData.append("invert", String(request.invert));
  formData.append("brightness", String(request.brightness));
  formData.append("contrast", String(request.contrast));
  formData.append("dithering", String(request.dithering));

  const response = await fetch(`${API_BASE_URL}/api/v1/convert`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Image conversion failed");
  }

  return response.json();
}
