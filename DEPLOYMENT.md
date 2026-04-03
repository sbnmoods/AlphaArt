# Deployment Guide

This project is split into two deployable services:

- `frontend` - Next.js app
- `backend` - FastAPI app

The simplest public deployment path is:

1. Deploy the frontend to Vercel
2. Deploy the backend to Render
3. Set the frontend API URL and backend allowed origins with environment variables

## Frontend on Vercel

### Project settings

- Root directory: `frontend`
- Framework preset: `Next.js`
- Install command: `npm install`
- Build command: `npm run build`
- Output setting: default for Next.js

### Required environment variable

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.onrender.com
```

## Backend on Render

Create a new Web Service with these settings:

- Root directory: `backend`
- Runtime: `Python`
- Build command: `pip install -e .`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Required environment variable

```text
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

If you use a custom domain or preview domains, add them as a comma-separated list:

```text
ALLOWED_ORIGINS=https://alphaart.vercel.app,https://www.alphaart.app
```

## Recommended deployment order

1. Deploy the backend first and copy its public URL
2. Add that backend URL to the frontend as `NEXT_PUBLIC_API_BASE_URL`
3. Deploy the frontend and copy its public URL
4. Add that frontend URL to the backend as `ALLOWED_ORIGINS`
5. Redeploy the backend if needed so the final origin list is active

## Smoke test after deployment

1. Open the frontend URL
2. Upload one of the sample images from `docs/examples`
3. Generate output in `Minimal ASCII` mode
4. Download SVG or PNG and confirm the request succeeds
5. Check the backend `/health` endpoint separately

## Common deployment issues

### CORS errors

Cause: frontend domain is not included in `ALLOWED_ORIGINS`

Fix: add the exact frontend origin to `ALLOWED_ORIGINS`

### Broken frontend requests

Cause: `NEXT_PUBLIC_API_BASE_URL` still points to localhost

Fix: update the environment variable to the deployed backend URL and redeploy the frontend

### 413 upload errors

Cause: source image is too large

Fix: use smaller images for the first public deployment or add image downscaling before upload