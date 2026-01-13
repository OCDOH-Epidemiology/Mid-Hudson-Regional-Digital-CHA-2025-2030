# Adding Citations to QMD Files

This script adds citations and references to QMD files in the same format as `01-introduction.qmd`.

## Format

The script converts citation markers like `[7]` to superscript links:
```html
<a href="#cite-7" title="Full citation text"><sup>7</sup></a>
```

And creates a references section:
```markdown
## References

<details>
<summary><strong>Click to view citations</strong></summary>

<span id="cite-7">7. Full citation text with <https://url.com></span>

</details>
```

## Usage

### Option 1: From JSON File (Recommended)

1. Create a JSON file with your citations:
```json
{
  "7": "US Census Bureau; American Community Survey, 2023 American Community Survey 5-Year Estimates, https://data.census.gov/table/..., April 2025",
  "8": "Another citation here",
  "9": "Yet another citation"
}
```

2. Run the script:
```bash
python scripts/add_citations.py chapters/03-demographics.qmd --citations citations.json
```

### Option 2: From DOCX File

```bash
python scripts/add_citations.py chapters/03-demographics.qmd --docx "source/2025 Regional CHA Document Orange County 12.17.2025.docx"
```

The script will automatically extract the references section from the DOCX file.

### Option 3: From PDF File

```bash
python scripts/add_citations.py chapters/03-demographics.qmd --pdf "source/document.pdf"
```

The script will automatically extract the references section from the PDF file.

## Steps

1. **Add citation markers to your QMD file**: 
   - Where you want a citation, add `[7]`, `[8]`, etc.
   - Example: `The population grew 4.7% from 2010 to 2020.[7]`

2. **Provide citations**:
   - Create a JSON file with citation numbers and text, OR
   - Provide a DOCX or PDF file with a references section

3. **Run the script**:
   ```bash
   python scripts/add_citations.py chapters/your-file.qmd --citations citations.json
   ```

4. **Review the output**:
   - Citations are now superscript links
   - References section is created at the end

## Example

**Before:**
```markdown
The population grew 4.7% from 2010 to 2020.[7]
```

**After:**
```markdown
The population grew 4.7% from 2010 to 2020.<a href="#cite-7" title="US Census Bureau; American Community Survey, 2023..."><sup>7</sup></a>
```

**References section added:**
```markdown
## References

<details>
<summary><strong>Click to view citations</strong></summary>

<span id="cite-7">7. US Census Bureau; American Community Survey, 2023 American Community Survey 5-Year Estimates, <https://data.census.gov/table/...>, April 2025</span>

</details>
```

## Notes

- The script will **not** overwrite existing references sections
- Citation markers must be in the format `[1]`, `[2]`, etc.
- URLs in citations are automatically formatted as `<https://...>`
- The format matches exactly what's used in `01-introduction.qmd`

