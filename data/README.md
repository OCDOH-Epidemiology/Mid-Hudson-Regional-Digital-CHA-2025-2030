# Data Layout and Updates

## Folder Structure
- `data/raw/`: Place raw Excel or CSV files here (ignored by git).
- `data/processed/`: Cleaned outputs used by the Quarto book.

## Updating Data
1. Add or replace `data/raw/cha_metrics.xlsx`.
2. Ensure the Excel file has sheets named `metrics` and `table`:
   - `metrics` columns: `year`, `metric`, `value`, `county`
   - `table` columns: `indicator`, `county`, `value`, `year`
3. Run `python scripts/build_data.py` to refresh `data/processed/` outputs.
4. Render the book: `quarto render`.

## Notes
- If the raw file is missing, the build script generates a small sample dataset so the book renders.
- Replace sample metrics with final indicators before publishing.
