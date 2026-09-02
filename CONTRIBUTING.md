# Contributing to enlace-python

## Layout

- `packages/enlace-fastapi/` — the FastAPI adapter, packaged as the `enlace-fastapi` PyPI
  distribution (import name `enlace_fastapi`)
- `packages/enlace-fastapi/tests/` — unit tests
- `scripts/dev-sync-ui.sh <package-dir> [path-to-enlace-ui-checkout]` — local dev: builds
  `@get-enlace/ui` from a checkout and copies its `dist/` into that package's
  `src/<import_pkg>/ui_embedded/`
- `scripts/ci-fetch-ui.sh <package-dir> <dist-tag-or-version> [registry-url]` — CI: fetches
  `@get-enlace/ui`'s published tarball, from GitHub Packages (dev) or npmjs.org (prod), and
  does the same (curl + tar, no Node)
- `packages/enlace-fastapi/ui-version.txt` — the pinned `@get-enlace/ui` version a prod
  release would embed; not yet wired into any release automation (see Status below)

Both scripts are shared across every package under `packages/` (unlike `enlace-dotnet`/
`enlace-java`, which are single-package repos and hardcode one destination) — a new adapter
(e.g. `enlace-flask`) reuses them as-is, no per-package copy needed.

## Development

This repo is a [`uv` workspace](https://docs.astral.sh/uv/concepts/workspaces/) — one
resolved environment across every package under `packages/*`, same role as `enlace-js`'s npm
workspace.

```bash
uv sync --all-packages --dev
uv run ruff check .
uv run mypy packages
uv run pytest
```

Run a single package's tests: `uv run --package enlace-fastapi pytest`.

## Local development against `@get-enlace/ui`

Each package's `src/<import_pkg>/ui_embedded/` (its embedded static assets, shipped as PyPI
package data) is never committed — it's a build artifact, populated one of two ways:

- **`scripts/dev-sync-ui.sh enlace-fastapi [path-to-enlace-ui-checkout]`** — builds
  `@get-enlace/ui` from a local checkout and copies its `dist/` output in, so you can
  sanity-check the real embedded-package-data path before a release without touching the
  registry.
- **CI** (`scripts/ci-fetch-ui.sh`) — fetches the published tarball instead, once CI exists
  for this (see Status below).

## Adding a new adapter (e.g. Flask)

1. `packages/enlace-<framework>/` with its own `pyproject.toml` (`name = "enlace-<framework>"`,
   `packages = ["src/enlace_<framework>"]`), mirroring `enlace-fastapi`'s layout.
2. `uv sync --all-packages` picks it up automatically — `[tool.uv.workspace] members =
   ["packages/*"]` at the repo root needs no change.
3. Reuse `scripts/dev-sync-ui.sh`/`ci-fetch-ui.sh` as-is (see above).
4. Update this repo's root `README.md` and, separately, `get-enlace.github.io`'s
   `docs/adapters/` per the workspace root `CLAUDE.md`.

## CI/CD

Two workflows under `.github/workflows/`, mirroring `enlace-dotnet`'s per-package pattern:

- **`build.yml`** — every PR into `main`: lint (`ruff`), typecheck (`mypy`), test (`pytest`)
  across the whole workspace.
- **`enlace-fastapi.yml`** — two triggers: push to `main` (path-filtered to
  `packages/enlace-fastapi/**`, `ui-version.txt`, etc.), and `repository_dispatch:
  enlace-ui-release`, fired by `enlace-ui`'s own release workflow whenever it publishes — this
  package is an **embedding-based** adapter, so it must actively rebuild and republish on
  every `enlace-ui` change, or consumers stay frozen on an old bundle. No manual
  `workflow_dispatch` escape hatch — a forced rebuild is just a commit pushed to `main`.

  `handle-ui-release` only runs for a *production* dispatch (a dev dispatch is a no-op here)
  and does exactly one thing: pins the incoming version into `ui-version.txt` and commits it.

  `deploy-dev` runs **unconditionally** on every trigger, fetching whatever's currently under
  `@get-enlace/ui`'s floating `dev` dist-tag on GitHub Packages, builds an
  `X.Y.Z.dev<run id>` release (PEP 440's dev-release syntax — the closest equivalent to npm's
  floating `dev` dist-tag PyPI actually has), and publishes it to **TestPyPI**.

  `deploy-prod` (gated behind the `production` environment's required-reviewer approval)
  refuses to run unless `ui-version.txt` holds a real pinned version, then fetches that exact
  `@get-enlace/ui` bundle from npmjs.org (not GitHub Packages — this is the prod path), builds
  and publishes whatever version is currently committed in `pyproject.toml` to **PyPI**, tags
  the release, and commits the next patch version bump.

  Both publish steps use **`uv publish --trusted-publishing always`** — PyPI's Trusted
  Publishing (OIDC) exchanges this job's GitHub Actions identity for a short-lived upload
  token at publish time, no stored API key needed. Nothing long-lived is stored in this repo;
  the trust relationship lives entirely in the Trusted Publisher policy configured on PyPI's
  (and TestPyPI's) side.

### One-time setup this needs

The workflow above is written and tested locally (`uv version`/`uv build` steps run clean
against a real build), but three things outside this repo still need to happen before it can
actually run end to end:

- **On GitHub** (repo → **Settings → Environments**): a `development` environment and a
  `production` environment, the latter with a required reviewer. `GITHUB_TOKEN` (used for the
  GitHub Packages dev-tag fetch) is automatic — no secret to add.
- **On PyPI** (**Your projects → Publishing**) and **TestPyPI** separately: a Trusted
  Publisher policy for a project named `enlace-fastapi`, each pointing at —
  Owner: `get-enlace`, Repository: `enlace-python`, Workflow name: `enlace-fastapi.yml`,
  Environment name: `production` (PyPI) / `development` (TestPyPI). PyPI allows registering
  this as a *pending* publisher before the project's first release exists yet.
- **On `enlace-ui`**: add this repo as a `repository_dispatch: enlace-ui-release` target
  (currently only fires for `enlace-js`/`enlace-dotnet`) — a separate change, in that repo.

Until all three are done, `deploy-dev`/`deploy-prod` will fail at the `uv publish` step (no
Trusted Publisher policy to exchange the OIDC token against) — expected, not a bug in the
workflow itself.
