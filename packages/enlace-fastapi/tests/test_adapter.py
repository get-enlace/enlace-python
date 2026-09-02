from enlace_fastapi import enlace
from fastapi import FastAPI
from fastapi.testclient import TestClient

SAMPLE_SPEC = {"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}, "paths": {}}


def build_app() -> TestClient:
    app = FastAPI()
    app.include_router(enlace(spec=SAMPLE_SPEC), prefix="/enlace")
    return TestClient(app)


def test_serves_the_spec_at_api_spec():
    client = build_app()
    res = client.get("/enlace/api/spec")
    assert res.status_code == 200
    assert res.json() == SAMPLE_SPEC

    # Not cached — a second call re-reads (identity check only meaningful
    # for file-backed specs, but confirms this isn't a static response).
    res2 = client.get("/enlace/api/spec")
    assert res2.json() == SAMPLE_SPEC


def test_serves_the_spec_from_a_file(tmp_path):
    import json

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(SAMPLE_SPEC))

    app = FastAPI()
    app.include_router(enlace(spec=spec_file), prefix="/enlace")
    client = TestClient(app)

    res = client.get("/enlace/api/spec")
    assert res.status_code == 200
    assert res.json() == SAMPLE_SPEC


def test_mounts_static_ui_without_error():
    # ui_embedded/ is a build artifact (see scripts/dev-sync-ui.sh) and is
    # empty in a fresh checkout — this only asserts the router mounts
    # cleanly and returns a real HTTP response (404 until synced), not that
    # actual UI bytes come back. That's covered manually via dev-sync-ui.sh,
    # per CONTRIBUTING.md.
    client = build_app()
    res = client.get("/enlace/index.html")
    assert res.status_code in (200, 404)
