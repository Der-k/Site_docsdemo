# AAEMI SiteLog Demo

Presentation prototype of an HSE / site management platform. Fictional data only.

## Run (Windows, Python 3.12)
```
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. Use **Reset demo data** in the top bar to restore the seed before a presentation.

## Layout
routes (`app/web`) -> services -> repositories -> `app/data/storage.py` (JSON file, atomic writes).
Dashboard figures and compliance statuses are always computed from records, never stored.

## AI assistant with Groq
Copy `.env.example` to `.env` and set `GROQ_API_KEY` (and `GROQ_MODEL` if you want a different model), then restart the server.
With no key, or with `ASSISTANT_PROVIDER=demo`, the offline demo assistant is used. If Groq is unreachable the app falls back to the demo assistant automatically.
The model can only propose changes; nothing is applied until you press Confirm. Keep `.env` out of version control.

## Hosting on Render (free)
1. Push this folder to a GitHub repo (`.env` and `demo_data.json` are git-ignored).
2. On Render: New > Blueprint, pick the repo. It reads `render.yaml`. When asked, enter a `DEMO_PASSWORD`.
3. Open the URL a few minutes before presenting: free instances sleep after 15 minutes idle and take up to a minute to wake.
4. Optional: add `GROQ_API_KEY` under Environment to enable the live AI assistant on the public site. Anyone with the demo password can then use your Groq quota.

Notes: the free disk is temporary, so data returns to the seed whenever the app restarts. All visitors share one dataset.
If the build rejects the Python version, change `PYTHON_VERSION` in `render.yaml` and `.python-version` to a 3.12.x release Render lists.
