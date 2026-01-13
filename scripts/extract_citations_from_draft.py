#!/usr/bin/env python3
"""
Extract citations from draft.md file and create a JSON file.

This script parses the draft.md file to extract citation references
in the format [^7]: ... and converts them to JSON format for use
with add_citations.py.

Usage:
    python scripts/extract_citations_from_draft.py
    python scripts/extract_citations_from_draft.py --output citations.json
"""

import re
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def extract_citations_from_markdown(md_path: Path) -> dict:
    """Extract citations from markdown file with [^N]: format."""
    if not md_path.exists():
        print(f"Error: Markdown file not found at {md_path}")
        return {}
    
    citations = {}
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match [^N]: citation text (may span multiple lines)
    # Format: [^7]: Text here, possibly with <https://url.com>, accessed date
    pattern = r'\[\^(\d+)\]:\s*((?:[^\n]|\n(?!\[\^))+)'
    
    matches = re.finditer(pattern, content, re.MULTILINE)
    
    for match in matches:
        cit_num = int(match.group(1))
        cit_text = match.group(2)
        
        # Clean up the text: remove extra whitespace, handle line breaks
        cit_text = ' '.join(cit_text.split())
        
        # Remove markdown link formatting if present, keep URLs
        cit_text = re.sub(r'<([^>]+)>', r'\1', cit_text)  # Remove angle brackets but keep content
        
        citations[cit_num] = cit_text
    
    return citations


def main():
    parser = argparse.ArgumentParser(
        description="Extract citations from draft.md to JSON format"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="draft/draft.md",
        help="Path to markdown file (default: draft/draft.md)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path (default: citations_from_draft.json)"
    )
    
    args = parser.parse_args()
    
    # Set up paths
    md_path = Path(args.input)
    if not md_path.is_absolute():
        md_path = PROJECT_ROOT / md_path
    
    output_path = Path(args.output) if args.output else PROJECT_ROOT / "scripts" / "citations_from_draft.json"
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    
    # Extract citations
    print(f"Extracting citations from {md_path}...")
    citations = extract_citations_from_markdown(md_path)
    
    if not citations:
        print("No citations found. Make sure the file uses [^N]: format.")
        return
    
    # Convert to string keys for JSON
    citations_json = {str(k): v for k, v in sorted(citations.items())}
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(citations_json, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Extracted {len(citations)} citations")
    print(f"✓ Saved to {output_path}")
    print(f"\nYou can now use this file with add_citations.py:")
    print(f"  python scripts/add_citations.py chapters/your-file.qmd --citations {output_path}")


if __name__ == "__main__":
    main()

