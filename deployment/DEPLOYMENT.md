# SmartHistory Deployment Guide (Current Stage)

This guide focuses on what is implemented and practical now:
- Local development for backend (FastAPI) and frontend (Next.js)
- Docker Compose for a simple containerized run
- Static hosting of the frontend on GitHub Pages (project site)

Cloud/Kubernetes stacks and advanced monitoring are out of scope here until we wire them up end-to-end.

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- SQLite for local dev (file is created automatically)
- Docker + Docker Compose (optional, for containerized run)

## Local Development

- Unified script: `./runner/deploy.sh local`
  - Starts FastAPI backend on `http://localhost:8000`
  - Starts Next.js frontend on `http://localhost:5173`

Manual start:
- Backend: `cd src/backend && python start.py development`
- Frontend: `cd src/frontend && npm run dev`

Environment variables for backend (example `.env.development` in `src/backend`):
```
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///./smarthistory_dev.db
LOG_LEVEL=DEBUG
```

## Docker Compose (Dev/Single-host)

Files:
- `deployment/docker-compose.yml` (dev)
- `deployment/docker-compose.prod.yml` (single-host prod-like)

Commands:
```
cd deployment
docker compose up -d --build                # dev compose
# or
docker compose -f docker-compose.prod.yml up -d --build
```

Endpoints (default):
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

## GitHub Pages (Frontend Only)

Goal: Publish the static Next.js frontend via GitHub Pages. The backend must be reachable at a public URL (self-hosted or a tunnel) and the frontend must point to that API.

Limitations:
- GitHub Pages is static hosting. Server functions/SSR are not supported.
- Use static export of Next.js and configure a `basePath` when using a project site.

### 1) Frontend config for static export
We’ve configured Next.js to support optional static export with a base path.
- Build-time env:
  - `STATIC_EXPORT=true` to enable `next export`
  - `NEXT_PUBLIC_BASE_PATH=/<repo>` for project pages, or empty for user/org pages
  - `NEXT_PUBLIC_API_BASE_URL=https://your-api.example.com` so the UI can reach your backend

Build locally to verify:
```
cd src/frontend
NEXT_PUBLIC_API_BASE_URL=https://your-api.example.com \
NEXT_PUBLIC_BASE_PATH=/your-repo \
STATIC_EXPORT=true \
npm run export

# Output will be in out/
```

### 2) GitHub Actions workflow
We include a workflow that:
- Builds the static site with the correct base path
- Publishes `out/` to the `gh-pages` branch

Adjust `NEXT_PUBLIC_BASE_PATH`:
- Project pages (recommended): `/${{ github.event.repository.name }}`
- User/org pages (repo named `<user>.github.io`): set it to empty `""`

### 3) Enable Pages in the repo
- GitHub → Settings → Pages
- Source: Deploy from branch → `gh-pages` → `/` (root)

### 4) Backend URL configuration
- Ensure the backend is reachable at a public URL.
- Set `NEXT_PUBLIC_API_BASE_URL` to that URL before building.

## Production Notes (Incremental)
- Keep using SQLite until a managed Postgres is needed.
- Harden CORS and secrets when exposing the backend publicly.
- Add HTTPS via a reverse proxy (e.g., Nginx/Caddy) when hosting the API.

This document will evolve as we wire up additional environments and CI/CD.
