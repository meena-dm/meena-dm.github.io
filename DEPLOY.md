# Deploying this portfolio (GitHub Pages)

## How it's structured

- **`*.dc.html`** — your editable source (open these in your design tool).
- **`build.py`** — turns the source into a clean, static, dependency-free site.
- **`docs/`** — the generated site that actually gets deployed. **Don't edit by hand** — it's overwritten on every build.

The static pages have **no runtime**: no `support.js`, no React/Babel, no
client-side rendering. Just HTML + CSS (fonts load from Google Fonts). They load
instantly and are fully indexable.

## The everyday loop

```bash
# 1. edit the .dc.html files (in your design tool or an editor)
# 2. rebuild the static site
python3 build.py
# 3. commit & push
git add -A && git commit -m "Update portfolio" && git push
```

## First-time setup

```bash
cd "HCI researcher portfolio transition"
git init
git add -A
git commit -m "Portfolio: static build"
git branch -M main
# create an empty repo on github.com first, then:
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Build and deployment → Source: “Deploy
from a branch” → Branch: `main`, Folder: `/docs` → Save.**

Your site appears in ~1 minute at:

```
https://<you>.github.io/<repo>/
```

(All links are relative, so it works fine under that `/<repo>/` subpath.)

### Tip: a cleaner URL
Name the repo **`<you>.github.io`** and it serves at the root:
`https://<you>.github.io/`.

## Preview locally before pushing

```bash
python3 -m http.server -d docs 8000
# open http://localhost:8000
```

## Notes

- `docs/.nojekyll` is included so GitHub serves the files as-is.
- The favicon is an inline "MM" mark — no separate file needed.
- If you add a new page: drop it in `build.py`'s `PAGES` map (source file →
  output name, title, description), then rebuild.
- Custom domain: add a `CNAME` file to `docs/` (or set it in the Pages UI) and
  point your DNS at GitHub Pages.
