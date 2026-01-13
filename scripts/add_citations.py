#!/usr/bin/env python3
"""
Add citations and references to QMD files in the same format as introduction.qmd.

This script:
1. Converts citation markers [1], [2], etc. to superscript links
2. Creates a references section matching the format in introduction.qmd
3. Can extract citations from PDF or DOCX files

Usage:
    python scripts/add_citations.py chapters/03-demographics.qmd --citations citations.json
    python scripts/add_citations.py chapters/03-demographics.qmd --docx "source/document.docx"
    python scripts/add_citations.py chapters/03-demographics.qmd --pdf "source/document.pdf"
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, Optional
import argparse

PROJECT_ROOT = Path(__file__).parent.parent


def extract_citations_from_json(json_path: Path) -> Dict[int, str]:
    """Extract citations from a JSON file."""
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        return {}
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            citations = json.load(f)
        # Convert string keys to integers
        return {int(k): str(v) for k, v in citations.items()}
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return {}


def extract_citations_from_docx(docx_path: Path) -> Dict[int, str]:
    """Extract citations from a DOCX file."""
    try:
        from docx import Document
    except ImportError:
        print("Error: python-docx not installed. Install with: pip install python-docx")
        return {}
    
    if not docx_path.exists():
        print(f"Error: DOCX file not found at {docx_path}")
        return {}
    
    try:
        doc = Document(docx_path)
        citations = {}
        in_references = False
        current_ref_num = None
        current_ref_text = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            
            # Check if we're entering the references section
            if "reference" in text.lower() and len(text.split()) < 5:
                in_references = True
                continue
            
            if in_references:
                # Look for numbered references (e.g., "1.", "2.", etc.)
                ref_match = re.match(r'^(\d+)\.\s*(.+)$', text)
                if ref_match:
                    # Save previous reference if exists
                    if current_ref_num is not None:
                        citations[current_ref_num] = ' '.join(current_ref_text).strip()
                    
                    # Start new reference
                    current_ref_num = int(ref_match.group(1))
                    current_ref_text = [ref_match.group(2)]
                elif current_ref_num is not None:
                    # Continue current reference (multi-line)
                    if text:
                        current_ref_text.append(text)
        
        # Save last reference
        if current_ref_num is not None:
            citations[current_ref_num] = ' '.join(current_ref_text).strip()
        
        print(f"Extracted {len(citations)} citations from DOCX file")
        return citations
        
    except Exception as e:
        print(f"Error extracting citations from DOCX: {e}")
        return {}


def extract_citations_from_pdf(pdf_path: Path) -> Dict[int, str]:
    """Extract citations from a PDF file."""
    try:
        import PyPDF2
    except ImportError:
        print("Error: PyPDF2 not installed. Install with: pip install PyPDF2")
        return {}
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return {}
    
    try:
        citations = {}
        in_references = False
        current_ref_num = None
        current_ref_text = []
        
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text = page.extract_text()
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Check if we're entering the references section
                    if "reference" in line.lower() and len(line.split()) < 5:
                        in_references = True
                        continue
                    
                    if in_references:
                        # Look for numbered references
                        ref_match = re.match(r'^(\d+)\.\s*(.+)$', line)
                        if ref_match:
                            # Save previous reference if exists
                            if current_ref_num is not None:
                                citations[current_ref_num] = ' '.join(current_ref_text).strip()
                            
                            # Start new reference
                            current_ref_num = int(ref_match.group(1))
                            current_ref_text = [ref_match.group(2)]
                        elif current_ref_num is not None:
                            # Continue current reference
                            if line:
                                current_ref_text.append(line)
        
        # Save last reference
        if current_ref_num is not None:
            citations[current_ref_num] = ' '.join(current_ref_text).strip()
        
        print(f"Extracted {len(citations)} citations from PDF file")
        return citations
        
    except Exception as e:
        print(f"Error extracting citations from PDF: {e}")
        return {}


def format_citation_link(cit_num: int, citation_text: str) -> str:
    """
    Format a citation as a superscript link matching introduction.qmd format.
    
    Format: <a href="#cite-1" title="Full citation text"><sup>1</sup></a>
    """
    # Escape quotes in citation text for HTML title attribute
    title_text = citation_text.replace('"', '&quot;')
    return f'<a href="#cite-{cit_num}" title="{title_text}"><sup>{cit_num}</sup></a>'


def convert_citation_markers(text: str, citations: Dict[int, str]) -> tuple[str, Dict[int, str]]:
    """
    Convert citation markers [1], [2], etc. to superscript links.
    
    Returns the converted text and a dict of citations actually used.
    """
    used_citations = {}
    
    # Pattern to find citation markers: [1], [2], etc.
    pattern = r'\[(\d+)\]'
    
    def replace_citation(match):
        cit_num = int(match.group(1))
        if cit_num in citations:
            used_citations[cit_num] = citations[cit_num]
            return format_citation_link(cit_num, citations[cit_num])
        # Keep original if citation not found
        return match.group(0)
    
    processed_text = re.sub(pattern, replace_citation, text)
    
    return processed_text, used_citations


def format_url_in_text(text: str) -> str:
    """Format URLs in citation text to match introduction.qmd format: <https://...>"""
    # Pattern to find URLs
    url_pattern = r'(https?://[^\s<>]+)'
    
    def replace_url(match):
        url = match.group(1)
        # Remove trailing punctuation that might not be part of URL
        url = url.rstrip('.,;:')
        return f'<{url}>'
    
    return re.sub(url_pattern, replace_url, text)


def create_references_section(used_citations: Dict[int, str]) -> str:
    """
    Create a references section matching the format in introduction.qmd.
    """
    if not used_citations:
        return ""
    
    # Sort by citation number
    sorted_citations = sorted(used_citations.items())
    
    references = ["## References", ""]
    references.append('<details>')
    references.append('<summary><strong>Click to view citations</strong></summary>')
    references.append("")
    
    for cit_num, ref_text in sorted_citations:
        # Format URLs in the reference text
        formatted_ref = format_url_in_text(ref_text)
        references.append(f'<span id="cite-{cit_num}">{cit_num}. {formatted_ref}</span>')
        references.append("")
    
    references.append('</details>')
    references.append("")
    
    return "\n".join(references)


def process_qmd_file(qmd_path: Path, citations: Dict[int, str]) -> None:
    """Process a QMD file to add citations and references."""
    if not qmd_path.exists():
        print(f"Error: QMD file not found at {qmd_path}")
        sys.exit(1)
    
    # Read the QMD file
    content = qmd_path.read_text(encoding='utf-8')
    
    # Check if references section already exists
    if re.search(r'^## References', content, re.MULTILINE):
        print("References section already exists. Skipping citation processing.")
        print("If you want to update citations, remove the existing references section first.")
        return
    
    if not citations:
        print("Warning: No citations provided. Cannot add citations.")
        return
    
    # Convert citation markers to superscript links
    content, used_citations = convert_citation_markers(content, citations)
    
    if used_citations:
        print(f"Converted {len(used_citations)} citations to superscript links")
        
        # Create references section
        references_section = create_references_section(used_citations)
        
        # Append references section to the end
        content = content.rstrip() + "\n\n" + references_section
        
        # Write back to file
        qmd_path.write_text(content, encoding='utf-8')
        print(f"✓ Processed and saved: {qmd_path}")
    else:
        print("No citation markers found in the text. Make sure you have [1], [2], etc. markers in your QMD file.")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Add citations and references to QMD files"
    )
    parser.add_argument(
        "qmd_file",
        type=str,
        help="Path to the QMD file to process"
    )
    parser.add_argument(
        "--citations",
        type=str,
        default=None,
        help="Path to JSON file with citations dictionary"
    )
    parser.add_argument(
        "--docx",
        type=str,
        default=None,
        help="Path to DOCX file to extract citations from"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="Path to PDF file to extract citations from"
    )
    
    args = parser.parse_args()
    
    qmd_path = Path(args.qmd_file)
    if not qmd_path.is_absolute():
        qmd_path = PROJECT_ROOT / qmd_path
    
    citations = {}
    
    # Extract citations from the specified source
    if args.citations:
        citations_path = Path(args.citations)
        if not citations_path.is_absolute():
            citations_path = PROJECT_ROOT / citations_path
        citations = extract_citations_from_json(citations_path)
    elif args.docx:
        docx_path = Path(args.docx)
        if not docx_path.is_absolute():
            docx_path = PROJECT_ROOT / docx_path
        citations = extract_citations_from_docx(docx_path)
    elif args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.is_absolute():
            pdf_path = PROJECT_ROOT / pdf_path
        citations = extract_citations_from_pdf(pdf_path)
    else:
        print("Error: Must specify --citations, --docx, or --pdf")
        parser.print_help()
        sys.exit(1)
    
    if not citations:
        print("Error: No citations extracted. Please check your source file.")
        sys.exit(1)
    
    # Process the QMD file
    process_qmd_file(qmd_path, citations)


if __name__ == "__main__":
    main()

