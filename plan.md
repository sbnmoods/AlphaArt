## AlphaArt Product and Technical Spec

AlphaArt is a web application that accepts a user-uploaded image and generates a character-based reconstruction of that image using alphabets, ASCII symbols, or other configured character sets. The recommended MVP is a two-part web system: a Next.js frontend for upload, controls, preview, and export, and a FastAPI backend for the canonical image-to-character conversion pipeline. Containerization is out of scope for the first pass and can be added later once the product and deployment shape are stable.

## Product goals

1. Let users upload a single image and convert it into readable, visually faithful character art.
2. Make the result easy to tune with a small number of meaningful controls.
3. Support export formats that are useful both for sharing and reuse.

## Target users

1. Designers and hobbyists creating stylized text art from images.
2. Developers and terminal enthusiasts who want ASCII or character-based output.
3. Casual users who want a simple upload-adjust-export workflow.

## MVP scope

1. Single-image upload via drag-and-drop or file picker.
2. Side-by-side original and generated output preview.
3. Preset character ramps such as dense ASCII, minimal ASCII, and alphanumeric.
4. Controls for output width, grayscale vs color mode, inversion, brightness, contrast, and optional dithering.
5. Export to plain text, SVG, and PNG.
6. Responsive UI for desktop and mobile.

## Out of scope

1. User accounts and authentication.
2. Saved projects or history.
3. Collaboration or sharing features.
4. Batch processing.
5. Video conversion.
6. Desktop packaging.
7. Containerization.

## Functional requirements

1. The app must accept PNG, JPEG, and WebP uploads.
2. The app must validate file type and size before processing.
3. The app must generate a character-based output from a source image using a configurable character ramp.
4. The app must support grayscale output and a color-preserving output mode.
5. The app must allow the user to adjust output width to control detail density.
6. The app must allow inversion so darker regions can map to lighter characters and vice versa.
7. The app must expose brightness and contrast controls that affect the conversion result.
8. The app should support optional dithering to improve tonal detail in some images.
9. The app must show a preview of the generated output before export.
10. The app must allow export as plain text, SVG, and PNG.

## Non-functional requirements

1. Typical web-sized images should convert in under 1 second for preview under normal development conditions.
2. Large images should fail gracefully with clear validation or be downscaled before processing.
3. Output rendering must preserve monospace alignment.
4. The API contract must be explicit and versionable.
5. The UI must remain responsive while processing is underway.

## Recommended tech stack

1. Frontend: Next.js, React, TypeScript, Tailwind CSS.
2. Backend: FastAPI, Pillow, NumPy.
3. Optional later: OpenCV for more advanced preprocessing.
4. Testing: Playwright for end-to-end UI checks, pytest for backend and contract tests.

## System architecture

1. Frontend responsibilities:
Handle uploads, settings controls, preview display, export triggers, validation messaging, and responsive layout.
2. Backend responsibilities:
Normalize input images, resize to character grid, compute luminance or color values, apply optional preprocessing, map cells to characters, and render outputs.
3. Processing model:
The backend is the source of truth for final output quality. The frontend may do lightweight image inspection or downscaling to improve responsiveness, but should not own the authoritative conversion algorithm.

## Conversion pipeline

1. Validate image type, size, and dimensions.
2. Normalize orientation and decode the image.
3. Resize the image to a target grid based on requested output width and character aspect ratio.
4. Convert image data into luminance cells or color cells.
5. Apply optional preprocessing such as brightness, contrast, inversion, and dithering.
6. Map each cell to a character from the selected ramp.
7. Produce a shared intermediate layout model.
8. Render the layout model into text, SVG, or PNG.

## Rendering spec

1. Text output:
Plain monospace text for copy/paste and terminal-friendly usage.
2. SVG output:
Primary visual export because it preserves layout, scales cleanly, and supports color.
3. PNG output:
Raster export generated from the same layout model for easy sharing.

## Frontend UX

1. Upload area with drag-and-drop and file picker fallback.
2. Control panel with presets and advanced options.
3. Side-by-side original and generated preview.
4. Loading/progress state during conversion.
5. Export actions for text, SVG, and PNG.
6. Clear error states for invalid uploads or failed conversions.

## API contract

1. Primary request payload fields:
Uploaded image, output width, character preset, color mode, inversion flag, brightness, contrast, dithering flag, and desired export format.
2. Primary response payload fields:
Normalized metadata, effective conversion settings, grid dimensions, preview artifact, and export-ready output or output URLs depending on final implementation choice.
3. Validation:
Reject unsupported file formats, oversized payloads, invalid widths, unsupported presets, and malformed parameter values with structured errors.

## Project structure

1. Frontend app under `frontend`
2. Backend service under `backend`
3. Shared documentation and setup instructions in `README.md`

## Relevant files

1. `c:\Dev\AlphaArt\frontend\package.json` for frontend dependencies and scripts.
2. `c:\Dev\AlphaArt\frontend\src\app\...` for page routes and shells.
3. `c:\Dev\AlphaArt\frontend\src\components\...` for upload, controls, preview, and export UI.
4. `c:\Dev\AlphaArt\frontend\src\lib\api.ts` for typed backend API calls.
5. `c:\Dev\AlphaArt\backend\pyproject.toml` for backend dependencies and tooling.
6. `c:\Dev\AlphaArt\backend\app\main.py` for FastAPI entry point and route wiring.
7. `c:\Dev\AlphaArt\backend\app\schemas.py` for request and response models.
8. `c:\Dev\AlphaArt\backend\app\services\converter.py` for the conversion pipeline.
9. `c:\Dev\AlphaArt\backend\app\services\renderers\...` for text, SVG, and PNG renderers.
10. `c:\Dev\AlphaArt\backend\tests\...` for API and pipeline tests.
11. `c:\Dev\AlphaArt\README.md` for setup and architecture notes.

## Implementation sequence

1. Freeze MVP controls and API contract.
2. Build backend conversion pipeline and SVG renderer first.
3. Build frontend upload and preview flow against the fixed contract.
4. Add text and PNG export.
5. Add validation, presets, and performance tuning.
6. Add deployment setup later, without introducing containers yet.

## Verification

1. Add backend tests for schema validation and negative cases.
2. Add fixture-based tests to verify stable character mapping and renderer correctness.
3. Add frontend tests for upload, parameter changes, preview refresh, and exports.
4. Benchmark small, medium, and large images for latency and memory use.
5. Manually verify responsive behavior on desktop and mobile.
6. Verify local non-container development setup for frontend and backend independently.