# enlace-python

Python framework adapters for [Enlace](https://github.com/get-enlace/enlace-ui) — a visual,
chained-execution canvas for any OpenAPI-documented API. Docs and the full picture of what
Enlace is: [get-enlace.github.io](https://get-enlace.github.io/).

Each adapter in this repo is a thin, idiomatic package for its own framework: it serves your
OpenAPI document and the canvas UI's static bundle, and nothing else — wiring up a chain,
running it, and holding credentials all happen client-side, in the browser.

## What's in this repo

A [`uv` workspace](https://docs.astral.sh/uv/concepts/workspaces/) — one Python package per
framework adapter, all living under `packages/`:

| Package | PyPI | What it's for |
|---|---|---|
| [`packages/enlace-fastapi`](packages/enlace-fastapi) | [`enlace-fastapi`](packages/enlace-fastapi/README.md) | FastAPI adapter |

More planned: Flask, evaluated once the FastAPI adapter is solid. See each package's own README
for install/usage instructions — this file only covers the repo as a whole.

## Using `uv`

Install [`uv`](https://docs.astral.sh/uv/) if you don't already have it, then from the repo
root:

```bash
uv sync --all-packages --dev   # installs every package + dev tooling into one environment
uv run pytest                  # run every package's tests
uv run ruff check .            # lint
uv run mypy packages           # typecheck
```

Run a single package's tests: `uv run --package enlace-fastapi pytest`.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for local development setup, how the embedded UI
bundle gets synced in, and how to add a new adapter package.

## License

[MIT](LICENSE)
