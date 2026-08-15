# Volo Health Care — Careers Concept

A concept rebuild of the Volo Health Care careers page (fixes the broken
page-builder shortcode bug on the live site) plus a working "Compatibility
Scan" chatbot that matches a visitor's skills against Volo's open roles,
backed by a FastAPI + Anthropic API endpoint.

## Structure

```
volo-demo/
├── api/
│   └── index.py      # FastAPI app — the /api/match endpoint
├── public/
│   ├── index.html     # Page markup
│   ├── styles.css      # Styling
│   └── script.js      # Frontend logic, calls /api/match
├── requirements.txt   # Python deps for the serverless function
└── vercel.json         # Routes /api/* to the Python function
```

## Deploy to Vercel

1. Push this folder to a GitHub repo (or drag-and-drop deploy from the
   Vercel dashboard).
2. In Vercel, import the project. It auto-detects the Python function in
   `api/` and serves everything in `public/` as static files.
3. In **Project Settings → Environment Variables**, add:
   - `ANTHROPIC_API_KEY` = your Anthropic API key
4. Deploy. Your site will be live at `your-project.vercel.app`.

The API key never touches the browser — the frontend only calls your own
`/api/match` endpoint, which holds the key server-side. This is the correct
pattern; never put the API key directly in frontend JavaScript.

## Run locally

```bash
pip install -r requirements.txt "uvicorn[standard]"
export ANTHROPIC_API_KEY=your-key-here
uvicorn api.index:app --reload --port 8000
```

Then serve `public/` with any static server (or just open `index.html`
directly and point `script.js`'s fetch URL at `http://localhost:8000/api/match`
for local testing — on Vercel the relative `/api/match` path works as-is).

## Notes

- Model used is `claude-sonnet-5`. Swap to a cheaper/faster model in
  `api/index.py` if you want lower latency or cost for a demo.
- The font is a plain system sans-serif (Helvetica Neue/Arial) to match the
  look of the live Volo site. If you know their exact font name, it's a
  one-line change in `public/styles.css` (`--font` variable).
- The visible "Concept rebuild" badge is intentional — worth keeping so it
  reads as a confident pitch rather than an attempt to pass this off as
  their real site.
