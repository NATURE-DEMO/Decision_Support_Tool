# Deployment

## Prerequisites

- **Python 3.12** (development) / **Python 3.11** (Docker production)
- [uv](https://docs.astral.sh/uv/) package manager
- Internet access (for OpenStreetMap, Nominatim, and Google Gemini APIs)
- `GEMINI_API_KEY` environment variable (Gemini AI features)

---

## Public access (Streamlit Community Cloud)

The production deployment is publicly accessible at **[nature-demo-dst.dic-cloudmate.eu](https://nature-demo-dst.dic-cloudmate.eu)**. No local installation is required for end users — open the URL in a browser. The application's landing page exposes two access tiers: the **General DST** (public, no sign-up required) and the **Integrated DST** (sign-up required — see [Authentication](user_guide/authentication.md) — which adds the pre-configured demonstrator-site configurations).

---

## Local development

```bash
# 1. Clone the repository
git clone https://github.com/NATURE-DEMO/Decision_Support_Tool.git
cd Decision_Support_Tool

# 2. Install dependencies
uv sync

# 3. Set the Gemini API key (optional — required for AI report features)
export GEMINI_API_KEY="your-api-key-here"

# 4. Run the Streamlit app
uv run streamlit run Home.py
```

The app is then accessible at `http://localhost:8501`.

---

## Docker (production-like)

```bash
# Build the image
docker build -t dst .

# Run the container
docker run -p 8501:8501 \
  -e GEMINI_API_KEY="your-api-key-here" \
  dst
```

The Dockerfile targets **Python 3.11** for production stability.

---

## Dependency management

Dependencies are managed with **uv**:

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata + runtime + dev dependencies |
| `uv.lock` | Locked dependency graph (commit this) |
| `requirements.txt` | Flat requirements for Docker build (keep in sync with `pyproject.toml`) |

To add a new dependency:

```bash
uv add <package>
# then update requirements.txt manually or via:
uv export --no-dev -o requirements.txt
```

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | For AI features | Google Gemini API key |
| `SUPABASE_URL` | For auth and snapshots | Supabase project URL |
| `SUPABASE_KEY` | For auth and snapshots | Supabase anon or service key |

For local development, create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```

For Streamlit Community Cloud, configure these in the **Secrets** settings panel of the Streamlit dashboard.

The clima-ind-viz API endpoint is hardcoded as `https://naturedemo-clima-ind.dic-cloudmate.eu` in the pages. To point to a local clima-ind-viz instance, update the `CLIMA_IND_VIZ_URL` constant in the relevant page files.

---

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific suites
uv run pytest tests/test_impact_models.py -v   # 20 tests — impact model YAML validation
uv run pytest tests/test_nbs.py -v             # 15 tests — NbS matrix integrity
```

Current status: **35 tests passing**.

---

## Linting and type checking

```bash
# Linting and formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy modules/ pages/ --ignore-missing-imports
```

Ruff configuration: `line-length = 100`, `ignore = ["E501"]`.

---

## Building the documentation

This documentation site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

```bash
# Install docs dependencies (once)
uv sync --extra docs

# Serve locally (auto-reload)
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

The generated site is in `site/`. To deploy to GitHub Pages:

```bash
uv run mkdocs gh-deploy
```
