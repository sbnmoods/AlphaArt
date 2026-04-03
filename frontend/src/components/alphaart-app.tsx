"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";

import { convertImage, type ConvertResponse } from "@/lib/api";

type Preset = "dense" | "minimal" | "alphanumeric";
type ColorMode = "grayscale" | "color";

const initialSettings = {
  outputWidth: 120,
  preset: "dense" as Preset,
  colorMode: "grayscale" as ColorMode,
  invert: false,
  brightness: 1,
  contrast: 1,
  dithering: false,
};

export function AlphaArtApp() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [settings, setSettings] = useState(initialSettings);
  const [result, setResult] = useState<ConvertResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null;
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setFile(nextFile);
    setResult(null);
    setError(null);
    if (nextFile) {
      setPreviewUrl(URL.createObjectURL(nextFile));
    } else {
      setPreviewUrl(null);
    }
  }

  function downloadFile(filename: string, content: BlobPart, mimeType: string) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function handleDownloadText() {
    if (!result) {
      return;
    }
    downloadFile("alphaart.txt", result.text, "text/plain;charset=utf-8");
  }

  function handleDownloadSvg() {
    if (!result) {
      return;
    }
    downloadFile("alphaart.svg", result.svg, "image/svg+xml;charset=utf-8");
  }

  function handleDownloadPng() {
    if (!result) {
      return;
    }

    const binary = atob(result.png_base64);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    downloadFile("alphaart.png", bytes, "image/png");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose an image before generating output.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const conversion = await convertImage({
        image: file,
        outputWidth: settings.outputWidth,
        preset: settings.preset,
        colorMode: settings.colorMode,
        invert: settings.invert,
        brightness: settings.brightness,
        contrast: settings.contrast,
        dithering: settings.dithering,
      });
      setResult(conversion);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Unexpected error");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">AlphaArt</p>
        <h1>Turn images into character art.</h1>
        <p className="lede">
          Upload an image, tune the mapping, and generate a text or SVG version through the AlphaArt API.
        </p>
      </section>

      <section className="grid">
        <form className="panel controls" onSubmit={handleSubmit}>
          <label className="field upload">
            <span>Source image</span>
            <input accept="image/png,image/jpeg,image/webp" type="file" onChange={handleFileChange} />
          </label>

          <label className="field">
            <span>Output width</span>
            <input
              min={20}
              max={300}
              type="range"
              value={settings.outputWidth}
              onChange={(event) =>
                setSettings((current) => ({ ...current, outputWidth: Number(event.target.value) }))
              }
            />
            <strong>{settings.outputWidth} columns</strong>
          </label>

          <label className="field">
            <span>Character preset</span>
            <select
              value={settings.preset}
              onChange={(event) =>
                setSettings((current) => ({ ...current, preset: event.target.value as Preset }))
              }
            >
              <option value="dense">Dense ASCII</option>
              <option value="minimal">Minimal ASCII</option>
              <option value="alphanumeric">Alphanumeric</option>
            </select>
          </label>

          <label className="field">
            <span>Color mode</span>
            <select
              value={settings.colorMode}
              onChange={(event) =>
                setSettings((current) => ({ ...current, colorMode: event.target.value as ColorMode }))
              }
            >
              <option value="grayscale">Grayscale</option>
              <option value="color">Color</option>
            </select>
          </label>

          <div className="inline-fields">
            <label className="checkbox">
              <input
                checked={settings.invert}
                type="checkbox"
                onChange={(event) =>
                  setSettings((current) => ({ ...current, invert: event.target.checked }))
                }
              />
              <span>Invert</span>
            </label>

            <label className="checkbox">
              <input
                checked={settings.dithering}
                type="checkbox"
                onChange={(event) =>
                  setSettings((current) => ({ ...current, dithering: event.target.checked }))
                }
              />
              <span>Dithering</span>
            </label>
          </div>

          <label className="field">
            <span>Brightness</span>
            <input
              min={0.5}
              max={1.5}
              step={0.1}
              type="range"
              value={settings.brightness}
              onChange={(event) =>
                setSettings((current) => ({ ...current, brightness: Number(event.target.value) }))
              }
            />
            <strong>{settings.brightness.toFixed(1)}</strong>
          </label>

          <label className="field">
            <span>Contrast</span>
            <input
              min={0.5}
              max={1.5}
              step={0.1}
              type="range"
              value={settings.contrast}
              onChange={(event) =>
                setSettings((current) => ({ ...current, contrast: Number(event.target.value) }))
              }
            />
            <strong>{settings.contrast.toFixed(1)}</strong>
          </label>

          <button className="primary" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Generating..." : "Generate artwork"}
          </button>

          {error ? <p className="error">{error}</p> : null}
        </form>

        <section className="panel previews">
          <div>
            <h2>Original</h2>
            {previewUrl ? <img alt="Uploaded preview" className="image-preview" src={previewUrl} /> : <p>No image selected.</p>}
          </div>

          <div>
            <h2>Generated</h2>
            {result ? (
              <>
                <div className="svg-preview" dangerouslySetInnerHTML={{ __html: result.svg }} />
                <div className="actions">
                  <button className="secondary" onClick={handleDownloadText} type="button">
                    Download text
                  </button>
                  <button className="secondary" onClick={handleDownloadSvg} type="button">
                    Download SVG
                  </button>
                  <button className="secondary" onClick={handleDownloadPng} type="button">
                    Download PNG
                  </button>
                </div>
                <details>
                  <summary>Plain text output</summary>
                  <pre>{result.text}</pre>
                </details>
                <p className="meta">
                  {result.metadata.grid_columns} x {result.metadata.grid_rows} grid from {result.metadata.original_width} x {result.metadata.original_height}
                </p>
              </>
            ) : (
              <p>Generate artwork to preview the API response.</p>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}
