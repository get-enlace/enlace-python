# enlace-fastapi

FastAPI adapter for [Enlace](https://github.com/get-enlace/enlace-ui) — a visual,
chained-execution canvas for any OpenAPI-documented API. Drag operations from your API onto a
canvas, wire one call's output into the next call's input, and run the whole chain from the
browser. Docs and the full picture of what Enlace is: [get-enlace.github.io](https://get-enlace.github.io/).

This adapter's job is intentionally small: it serves your OpenAPI document and the canvas UI's
static bundle. Nothing else — wiring up a chain, running it, and holding credentials all happen
client-side, in the browser, once the page loads.

## Install

```bash
pip install enlace-fastapi
```

## Usage

```python
from fastapi import FastAPI
from enlace_fastapi import enlace

app = FastAPI()
app.include_router(enlace(spec="./openapi.json"), prefix="/enlace")
```

Open `/enlace` and the canvas loads, reading your spec from `/enlace/api/spec`.

`spec` is a file path (`.json`/`.yaml`/`.yml`) or an already-parsed OpenAPI 3.x `dict` —
whatever's easiest to point at your API's own document.

## Using FastAPI's own generated spec

Already have FastAPI building your OpenAPI document from your routes? Call `app.openapi()`
yourself and pass the result straight through — no separate export step:

```python
from fastapi import FastAPI
from enlace_fastapi import enlace

app = FastAPI(title="My API", version="1.0.0")

# ... your routes ...

app.include_router(enlace(spec=app.openapi()), prefix="/enlace")
```

`app.openapi()` builds (and caches) the schema from your routes, so call it after they're
registered. Already mounting `/docs` or `/redoc` from the same app? Nothing about mounting
`enlace()` changes how those keep working — they're independent consumers of the same spec.

## How it works

`enlace(spec=...)` returns a plain `APIRouter` with two things mounted on it:

- **`GET /api/spec`** — resolves `spec` and returns it as JSON, read fresh on every request
  rather than cached once at startup, so editing a spec file on disk shows up on the next canvas
  reload with no restart needed.
- **The canvas UI's static assets**, at every other path under the router — this is a prebuilt
  bundle shipped inside the `enlace-fastapi` package itself, not fetched over the network at
  request time.

Everything past that — parsing the spec into operations, letting you wire a chain together,
actually sending requests to your API when you hit Run — happens in the browser, in the UI
bundle. This adapter never sees or proxies that traffic.

## Contributing

See [`CONTRIBUTING.md`](https://github.com/get-enlace/enlace-python/blob/main/CONTRIBUTING.md)
for local development setup.

## License

[MIT](https://github.com/get-enlace/enlace-python/blob/main/LICENSE)
