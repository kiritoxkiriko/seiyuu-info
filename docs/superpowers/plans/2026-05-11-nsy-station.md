# nsy 情报站 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Cloudflare-deployable voice actress information station for configurable Japanese female voice actors.

**Architecture:** The repository root is the Python Workers FastAPI backend project, with the Astro/React/Tailwind frontend isolated under `web/`. Backend code follows a standard FastAPI layout: `app/main.py` creates the app, `app/api/v1/endpoints/` owns routes, `app/core/` owns settings, `app/schemas/` owns Pydantic models, and `app/services/` owns repositories/providers. The frontend reads from the backend API and renders profile, gallery, event timeline, and SNS feeds.

**Tech Stack:** Astro, React, TypeScript, Tailwind CSS, Cloudflare Workers, Python Workers, FastAPI, Pydantic, pytest.

---

### Task 1: Project Structure

**Files:**
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `wrangler.jsonc`
- Create: `web/package.json`
- Create: `web/astro.config.mjs`
- Create: `web/tailwind.config.mjs`
- Create: `web/tsconfig.json`
- Create: `web/wrangler.jsonc`

- [x] Add workspace documentation and package metadata.
- [x] Configure Astro for Cloudflare Workers and Tailwind.
- [x] Configure Python Worker entry point and package dependencies.

### Task 2: Backend API

**Files:**
- Create: `app/main.py`
- Create: `app/api/v1/router.py`
- Create: `app/api/v1/endpoints/actors.py`
- Create: `app/api/v1/endpoints/health.py`
- Create: `app/core/config.py`
- Create: `app/schemas/voice_actor.py`
- Create: `app/services/repository.py`
- Create: `app/services/eventernote.py`
- Create: `app/services/sns.py`
- Create: `worker.py`
- Create: `data/actors.json`
- Create: `tests/test_api.py`

- [x] Define Pydantic models for actors, events, photos, and SNS posts.
- [x] Load configurable actor data from JSON.
- [x] Provide API routes for actor list/detail, events, and SNS posts.
- [x] Add provider functions for Eventernote parsing and SNS filtering.
- [x] Add API tests for config loading, routes, and repost/reply filtering.

### Task 3: Frontend Experience

**Files:**
- Create: `web/src/pages/index.astro`
- Create: `web/src/components/ActorDashboard.tsx`
- Create: `web/src/lib/api.ts`
- Create: `web/src/types.ts`
- Create: `web/src/styles/global.css`
- Create: `web/src/env.d.ts`

- [x] Build the first-screen dashboard with configured actor tabs.
- [x] Render profile, official photo, photo wall, event timeline, and SNS feed.
- [x] Add empty/error states and fallback sample data for local static preview.
- [x] Style with Tailwind using a dense editorial dashboard layout.

### Task 4: Verification

**Files:**
- Modify as needed based on verification results.

- [x] Run backend tests with `uv run pytest`.
- [ ] Run frontend install/build if dependencies are available.
- [x] Report any commands blocked by missing dependencies or network restrictions.
