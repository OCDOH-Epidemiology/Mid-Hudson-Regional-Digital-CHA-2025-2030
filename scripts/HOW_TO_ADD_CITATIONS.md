# How to Add Citations to Any QMD File

## Current Format (Same as Introduction)

Your citations in `03-demographics.qmd` already match the format in `01-introduction.qmd`:

**In the text:**
```html
<a href="#cite-7" title="Full citation text"><sup>7</sup></a>
```

**In the References section:**
```html
<span id="cite-7">7. Full citation text with <https://url.com></span>
```

## Steps to Add Citations to Another File

### Step 1: Add Citation Markers

In your `.qmd` file, add citation markers where you want citations:

```markdown
The population grew 4.7% from 2010 to 2020.[7]
Income affects health outcomes.[8]
```

### Step 2: Prepare Your Citations

**Option A: Use existing citations file**
```bash
# Use the demographics citations (7-11)
python scripts/add_citations.py chapters/your-file.qmd --citations scripts/demographics_citations.json
```

**Option B: Create your own JSON file**
Create `scripts/your_citations.json`:
```json
{
  "7": "United States Census Bureau, 2025, https://data.census.gov/..., accessed August 2025",
  "8": "Robert Wood Johnson Foundation, 2013, https://www.rwjf.org/..., accessed August 2025"
}
```

**Option C: Extract from draft.md**
```bash
# Extract all citations from draft.md
python scripts/extract_citations_from_draft.py --output scripts/all_citations.json

# Then use them
python scripts/add_citations.py chapters/your-file.qmd --citations scripts/all_citations.json
```

**Option D: Extract from DOCX/PDF**
```bash
# From DOCX
python scripts/add_citations.py chapters/your-file.qmd --docx "source/document.docx"

# From PDF  
python scripts/add_citations.py chapters/your-file.qmd --pdf "source/document.pdf"
```

### Step 3: Run the Script

```bash
# From project root directory
python scripts/add_citations.py chapters/your-file.qmd --citations scripts/your-citations.json
```

### Step 4: Done!

The script will:
- ✅ Convert `[7]` to `<a href="#cite-7"><sup>7</sup></a>`
- ✅ Add a References section at the end
- ✅ Format everything to match `01-introduction.qmd`

## Example: Adding Citations to a New Chapter

```bash
# 1. Edit your file and add markers
# chapters/04-your-chapter.qmd:
#   Some text here.[12]
#   More text.[13]

# 2. Extract citations from draft.md (if available)
python scripts/extract_citations_from_draft.py --output scripts/all_citations.json

# 3. Run the script
python scripts/add_citations.py chapters/04-your-chapter.qmd --citations scripts/all_citations.json

# 4. Check the output - citations are now formatted!
```

## What Gets Created

**Before:**
```markdown
The population grew 4.7% from 2010 to 2020.[7]
```

**After:**
```markdown
The population grew 4.7% from 2010 to 2020.<a href="#cite-7" title="United States Census Bureau, 2025, https://data.census.gov/..., accessed August 2025"><sup>7</sup></a>
```

**References section added at end:**
```markdown
## References

<details>
<summary><strong>Click to view citations</strong></summary>

<span id="cite-7">7. United States Census Bureau, 2025, <https://data.census.gov/...>, accessed August 2025</span>

</details>
```

## Notes

- The script **won't overwrite** existing references sections
- Citation markers must be `[7]` not `[ 7 ]` (no spaces)
- URLs are automatically formatted as `<https://...>`
- Format matches exactly what's in `01-introduction.qmd`

