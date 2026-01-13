# Quick Start: Adding Citations Automatically

## The Script Already Exists!

You have a script at `scripts/add_citations.py` that automates adding citations to QMD files.

## How to Use It

### Step 1: Prepare Your Citations

Create a JSON file with your citations. For example, `demographics_citations.json`:

```json
{
  "7": "United States Census Bureau, 2025, https://data.census.gov/..., accessed August 2025",
  "8": "Robert Wood Johnson Foundation, 2013, https://www.rwjf.org/..., accessed August 2025"
}
```

**Or** use the existing citations file:
- `scripts/demographics_citations.json` - Contains citations 7-11 from demographics chapter

### Step 2: Add Citation Markers to Your QMD File

In your `.qmd` file, add citation markers where needed:

```markdown
The population grew 4.7% from 2010 to 2020.[7]
Income can affect many aspects of life.[8]
```

### Step 3: Run the Script

```bash
# From the project root directory
python scripts/add_citations.py chapters/your-file.qmd --citations scripts/demographics_citations.json
```

### Step 4: Done!

The script will:
- ✅ Convert `[7]` to clickable superscript links
- ✅ Add a References section at the end
- ✅ Format everything to match `01-introduction.qmd`

## Alternative: Extract from Source Document

If you have a DOCX or PDF with a references section:

```bash
# From DOCX
python scripts/add_citations.py chapters/your-file.qmd --docx "source/document.docx"

# From PDF
python scripts/add_citations.py chapters/your-file.qmd --pdf "source/document.pdf"
```

## Example Workflow

```bash
# 1. Make sure you're in the project root
cd "Mid-HudsonRegionalCHA-2025"

# 2. Add citation markers [7], [8], etc. to your .qmd file
# (Edit the file manually)

# 3. Run the script
python scripts/add_citations.py chapters/03-demographics.qmd --citations scripts/demographics_citations.json

# 4. Check the output - citations are now linked!
```

## Notes

- The script **won't overwrite** existing references sections (safety feature)
- If you need to update citations, remove the `## References` section first
- Citation markers must be in format `[1]`, `[2]`, etc. (not `[1]` with spaces)
- URLs are automatically formatted as `<https://...>`

## Troubleshooting

**"No citations extracted"**
- Check that your JSON file has the correct format
- Make sure citation numbers match what's in your QMD file

**"References section already exists"**
- The script won't overwrite existing references
- Remove the `## References` section manually if you want to regenerate

**"No citation markers found"**
- Make sure you have `[7]`, `[8]`, etc. in your QMD file
- Check for typos or extra spaces

