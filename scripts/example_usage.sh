#!/bin/bash
# Example usage of citation automation scripts

# Example 1: Extract citations from draft.md and create JSON
echo "Example 1: Extracting citations from draft.md..."
python scripts/extract_citations_from_draft.py --output scripts/all_citations.json

# Example 2: Add citations to a QMD file using JSON
echo ""
echo "Example 2: Adding citations to a QMD file..."
echo "python scripts/add_citations.py chapters/your-file.qmd --citations scripts/demographics_citations.json"

# Example 3: Add citations from DOCX source
echo ""
echo "Example 3: Extracting and adding citations from DOCX..."
echo "python scripts/add_citations.py chapters/your-file.qmd --docx 'source/2025 Regional CHA Document Orange County 12.17.2025.docx'"

# Example 4: Add citations from PDF source
echo ""
echo "Example 4: Extracting and adding citations from PDF..."
echo "python scripts/add_citations.py chapters/your-file.qmd --pdf 'source/document.pdf'"

