# Workline CI Failure Analysis

## Commit

- **Base SHA:** `7c5038b78ac657dea3df110b884eff2d3d6d8f6c`
- **Branches:** `fix/ci-cd-failures`, `main`

## Backend

- **Workflow:** `Workline CI` (`.github/workflows/ci.yml`)
- **Run IDs:** `32587389735`, `32587293883`
- **Job:** `Backend Test Suite & Safety Checks`
- **Failing step:** `Run pytest test suite`
- **Command:** `python -m pytest tests -v`
- **First error:** Missing test and platform dependencies (`pytest-asyncio`, `numpy`, `fastapi`, `reportlab`, `python-docx`) when installed into isolated runner environment via `pip install -e ".[dev]"`.
- **Root cause:** `pyproject.toml` and `backend/requirements.txt` lacked explicit declarations for `pytest-asyncio` and dependencies required by tests during clean CI runner setup.

## Frontend

- **Workflow:** `Workline CI` (`.github/workflows/ci.yml`)
- **Run IDs:** `32587389735`, `32587293883`
- **Job:** `Frontend Build & Typecheck`
- **Failing step:** `Install and build frontend`
- **Command:** `npm ci` / `npm run build`
- **First error:** `npm ci` in `frontend/` directory conflicted with root monorepo workspace dependencies, and missing `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` during static Next.js Turbopack page evaluation in CI runner.
- **Root cause:** Monorepo installation needs to run at workspace root level (`npm install`), and CI environment needed build-time publishable key environment variable.

## Vercel

- **Deployment:** Vercel GitHub Integration
- **Failing step:** `Build & Output Directory Resolution`
- **Command:** `npm run build`
- **First error:** Vercel defaulted to expecting root `.next` output directory instead of monorepo `frontend/.next`.
- **Root cause:** Missing `vercel.json` monorepo configuration specifying output directory and workspace build command.

## Shared Root Causes

1. Missing monorepo configuration (`vercel.json`) connecting Vercel build output to `frontend/.next`.
2. Missing environment variable injection in CI workflows for Next.js build prerendering.
3. Isolated environment package dependency completeness in `pyproject.toml` and `backend/requirements.txt`.

## Independent Root Causes

1. `pytest-asyncio` missing from `[project.optional-dependencies] dev` in `pyproject.toml`.
2. Workspace root vs frontend subdirectory lockfile resolution in GitHub Actions runner.
