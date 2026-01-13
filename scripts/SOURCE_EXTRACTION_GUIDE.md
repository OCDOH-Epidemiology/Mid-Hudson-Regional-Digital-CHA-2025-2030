# Source Information Extraction Guide

When creating tables, you need to extract the correct source information from:
**`2025 Regional CHA Document Orange County 12.17.2025.docx`**

## What to Look For

For each table in the source document, identify:

1. **Table ID**: e.g., "S0101", "B03002", "S1601", "S1501", "S1901", "S2101", "S1810"
2. **Data Year**: Usually 2023, but may be 2020 or other years
3. **Estimate Type**: "5-Year Estimates" (capital) or "5-year estimates" (lowercase)
4. **URL**: The full Census Bureau data table URL
5. **Citation Date**: Usually "April 2025" but may vary

## Common Patterns

### Census Bureau Tables (Most Common)

**Format in source document:**
```
Source: US Census Bureau; American Community Survey, 2023 American Community Survey 5-Year Estimates, Table S0101, April 2025
https://data.census.gov/table/ACSST5Y2023.S0101?q=s0101&g=...
```

**Use in code:**
```python
from scripts.cha_table_styling import create_source_callout

source = create_source_callout(
    "S0101",  # From "Table S0101"
    "https://data.census.gov/table/ACSST5Y2023.S0101?q=s0101&g=...",  # Full URL
    data_year=2023,  # From "2023"
    estimate_type="5-Year Estimates",  # From "5-Year Estimates"
    citation_month="April",  # From "April"
    citation_year=2025  # From "2025"
)
```

### Different Year Example

**If source shows 2020:**
```python
source = create_source_callout(
    "S1810",
    "https://data.census.gov/table/...",
    data_year=2020,  # Different year
    estimate_type="5-year estimates"  # Note: lowercase
)
```

### Non-Census Sources

**If source is from NYS Department of Health or other agency:**
```python
source = create_source_callout(
    custom_text="New York State Department of Health, [Vital Statistics Data](https://...), 2025"
)
```

## Quick Checklist

For each table, verify:
- [ ] Table ID matches source document
- [ ] Data year is correct
- [ ] Estimate type matches (capitalization matters)
- [ ] URL is complete and correct
- [ ] Citation date matches source document
- [ ] Source callout uses `collapse="true"` for accordion format

## Example Workflow

1. **Find table in source document** (2025 Regional CHA Document Orange County 12.17.2025.docx)
2. **Locate the source citation** at the bottom of the table
3. **Extract information:**
   - Table ID: Look for "Table S0101" or "Table B03002"
   - Year: Look for "2023" or "2020" in the citation
   - URL: Copy the full URL from the document
4. **Generate source callout:**
   ```python
   from scripts.cha_table_styling import create_source_callout
   source = create_source_callout("S0101", "https://...", data_year=2023)
   print(source)
   ```
5. **Copy and paste** the output into your Quarto document

## Common Table IDs in CHA Document

Based on current usage:
- **S0101**: Population characteristics
- **B03002**: Race and ethnicity
- **S1601**: Spoken language
- **S1501**: Educational attainment
- **S1901**: Income
- **S2101**: Veteran status
- **S1810**: Disability

But always verify against the source document!

