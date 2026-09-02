"""FastAPI adapter for Enlace — mounts the canvas UI and the spec endpoint
it reads from.

    from fastapi import FastAPI
    from enlace_fastapi import enlace

    app = FastAPI()
    app.include_router(enlace(spec="openapi.json"), prefix="/enlace")

This adapter's job is deliberately small — per ARCHITECTURE.md's MVP model,
execution runs entirely client-side in @get-enlace/ui, so there's no
`/api/run` or `/api/credentials` here at all. All this does is:
  - serve the raw OpenAPI document (parsed into an Operation[] list
    client-side, not here — see @get-enlace/ui's engine/specParser.ts)
  - serve the built UI bundle

See CONTRIBUTING.md for how ui_embedded/ gets populated.
"""

from __future__ import annotations

from importlib import resources

from fastapi import APIRouter
from starlette.staticfiles import StaticFiles

from ._spec_loader import SpecSource, load_spec

__all__ = ["enlace", "SpecSource"]

__version__ = "0.0.1"


def enlace(spec: SpecSource) -> APIRouter:
    """Builds the router to mount at your chosen path, e.g.:

        app.include_router(enlace(spec=my_spec), prefix="/enlace")

    `spec` is the only input this needs — a file path (str/Path) to a
    .json/.yaml/.yml document, or an already-parsed dict — however it was
    produced (FastAPI's own `app.openapi()`, a hand-written file, anything).
    """
    router = APIRouter()

    @router.get("/api/spec")
    def get_spec() -> dict:
        # Read fresh on each request, not cached — matches the "not stored,
        # read fresh each load" rule from ARCHITECTURE.md §4.
        return load_spec(spec)

    # Static canvas UI bundle. Resolved via importlib.resources against this
    # installed package's own `enlace_fastapi/ui_embedded/` data, not a
    # relative path into this monorepo — so this works identically whether
    # `enlace-fastapi` got here via a `uv` workspace install (local dev) or
    # a real PyPI install of the built wheel. There's nothing to fetch at
    # import time; the directory must already be populated (see
    # scripts/dev-sync-ui.sh / scripts/ci-fetch-ui.sh at the repo root)
    # before this can serve anything beyond a 404.
    ui_dir = resources.files(__name__) / "ui_embedded"
    router.mount("/", StaticFiles(directory=str(ui_dir), html=True), name="enlace-ui")

    return router
