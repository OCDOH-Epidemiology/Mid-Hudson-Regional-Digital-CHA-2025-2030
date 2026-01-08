# Orange County Community Health Assessment (Quarto Book)

This repository contains a Quarto Book site for the Orange County Community Health Assessment (CHA), built with Python-only Jupyter execution.

## Quick Start
1. Install Python dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Build or refresh data outputs:
   ```bash
   python scripts/build_data.py
   ```
3. Render the book:
   ```bash
   quarto render
   ```
4. Open `docs/index.html` in a browser.

## Updating the Word Draft
Convert the source Word document to Markdown (and extract images):
```bash
scripts/convert_docx_to_md.sh
```
Then move narrative into the appropriate `chapters/*.qmd` files. See TODO markers for cleanup.

## Data Workflow
- Place raw Excel files in `data/raw/`.
- Run `python scripts/build_data.py` to generate `data/processed/` outputs.
- Charts and tables read exclusively from `data/processed/` to keep builds reproducible.

## Publishing to GitHub Pages
The book outputs to `docs/` for GitHub Pages.
1. Run `quarto render`.
2. Commit and push to `main`.
3. In GitHub: Settings -> Pages -> Build from branch `main`, folder `/docs`.

### Optional GitHub Actions
A workflow is provided in `.github/workflows/quarto-render.yml` to render and publish on push to `main`. Ensure GitHub Pages is configured to serve from the `gh-pages` branch if you enable the workflow, or adjust the workflow to target `/docs` directly.

## Scripts
- `scripts/build_data.py`: Build processed CSV/Parquet outputs from Excel.
- `scripts/convert_docx_to_md.sh`: Convert Word doc to Markdown draft.
- `scripts/smoke_test_render.sh`: Run `quarto render`.
