"""
CHA Table Styling Module

This module provides standardized table styling functions for the Community Health Assessment.
Use this module to ensure consistent table formatting across all chapters.

Usage:
    from scripts.cha_table_styling import style_cha_table
    
    df = pd.DataFrame(your_data)
    styled_table = style_cha_table(df)
    styled_table  # Display in Quarto
"""

import pandas as pd


def style_cha_table(df, has_multilevel_headers=False):
    """
    Apply consistent CHA table styling to a pandas DataFrame.
    
    Styling specifications:
    - Header: White background, bold, centered
    - Row 1: #EAF5DB (light green)
    - Row 2: White
    - Row 3: #EAF5DB (light green)
    - Alternates: white, #EAF5DB, white, #EAF5DB...
    - First column: Bold, left-aligned
    - Other columns: Center-aligned
    - Dark green separator line after "Westchester" row to separate county data from grouped areas
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to style
    has_multilevel_headers : bool, optional
        If True, applies special styling for MultiIndex column headers
        to create merged cell appearance (default: False)
        
    Returns
    -------
    pandas.io.formats.style.Styler
        A styled DataFrame ready for display in Quarto
        
    Example
    -------
    >>> import pandas as pd
    >>> from scripts.cha_table_styling import style_cha_table
    >>> 
    >>> data = {'Region': ['A', 'B'], 'Value': [100, 200]}
    >>> df = pd.DataFrame(data)
    >>> styled = style_cha_table(df)
    >>> styled  # Display in Quarto
    """
    styles = [
        # Header styling - white background
        {'selector': 'th', 'props': [
            ('font-weight', 'bold'), 
            ('text-align', 'center'), 
            ('background-color', '#FFFFFF'), 
            ('padding', '10px'),
            ('border', '1px solid #ddd')
        ]},
        # First column - bold, left-aligned
        {'selector': 'td:first-child', 'props': [
            ('font-weight', 'bold'), 
            ('text-align', 'left'), 
            ('padding', '10px'),
            ('border', '1px solid #ddd')
        ]},
        # Other columns - center-aligned
        {'selector': 'td:not(:first-child)', 'props': [
            ('text-align', 'center'), 
            ('padding', '10px'),
            ('border', '1px solid #ddd')
        ]},
        # Odd rows (1st, 3rd, 5th...) - light green
        {'selector': 'tbody tr:nth-child(odd)', 'props': [
            ('background-color', '#EAF5DB')
        ]},
        # Even rows (2nd, 4th, 6th...) - white
        {'selector': 'tbody tr:nth-child(even)', 'props': [
            ('background-color', '#FFFFFF')
        ]},
        # Table container
        {'selector': 'table', 'props': [
            ('border-collapse', 'collapse'), 
            ('width', '100%'), 
            ('margin', '20px 0'),
            ('font-size', '14px')
        ]}
    ]
    
    # Add MultiIndex header styling if needed
    if has_multilevel_headers and isinstance(df.columns, pd.MultiIndex):
        # Style for top-level headers (merged appearance)
        # Target all top-level header cells
        styles.append({
            'selector': 'thead tr:first-child th', 
            'props': [
                ('border-bottom', '2px solid #333'),
                ('font-weight', 'bold'),
                ('background-color', '#FFFFFF'),
                ('text-align', 'center'),
                ('vertical-align', 'middle'),
                ('padding', '10px')
            ]
        })
        # Style for second-level headers
        styles.append({
            'selector': 'thead tr:last-child th', 
            'props': [
                ('font-weight', 'normal'),
                ('font-size', '0.9em'),
                ('text-align', 'center'),
                ('background-color', '#FFFFFF'),
                ('padding', '10px')
            ]
        })
        # For MultiIndex, we need to handle the first column header separately
        styles.append({
            'selector': 'thead tr:first-child th:first-child', 
            'props': [
                ('text-align', 'left'),
            ]
        })
    
    # Find the row index where "Westchester" appears in the first column
    # and add a dark green border-bottom separator
    first_col = df.columns[0]
    
    # Create the styled table
    styled = df.style.set_table_styles(styles).hide(axis="index")
    
    # Add dark green border-bottom to the Westchester row if found
    # Dark green color: using a dark green shade
    dark_green = '#2d5016'  # Dark green color
    
    # Create a function to apply border-bottom to the Westchester row
    def add_border_bottom(row):
        # Check if this row contains "Westchester" in the first column
        # When axis=1, row is a Series with column names as index
        first_val = row[first_col] if first_col in row.index else None
        if pd.notna(first_val) and str(first_val).strip().lower() == 'westchester':
            return ['border-bottom: 3px solid ' + dark_green] * len(row)
        return [''] * len(row)
    
    # Apply the function to all rows
    styled = styled.apply(add_border_bottom, axis=1)
    
    return styled


def format_source_citation(table_id, url, data_year=2023, estimate_type="5-Year Estimates", citation_month="April", citation_year=2025, custom_text=None):
    """
    Create a standardized source citation with hyperlink.
    
    This is the STANDARD format for all CHA table sources.
    Flexible to handle different table IDs, years, and estimate types.
    
    Parameters
    ----------
    table_id : str
        The Census Bureau table ID (e.g., "S0101", "B03002", "S1601")
    url : str
        The full URL to the Census Bureau data table
    data_year : int, optional
        The data year (default: 2023)
    estimate_type : str, optional
        The estimate type - "5-Year Estimates" or "5-year estimates" (default: "5-Year Estimates")
    citation_month : str, optional
        The citation month (default: "April")
    citation_year : int, optional
        The citation year (default: 2025)
    custom_text : str, optional
        Custom citation text to use instead of standard format. If provided, 
        other parameters are ignored except url which should be embedded in custom_text.
        
    Returns
    -------
    str
        Formatted source citation in standard CHA format
        
    Examples
    --------
    >>> # Standard Census Bureau table
    >>> citation = format_source_citation(
    ...     "S0101",
    ...     "https://data.census.gov/table/ACSST5Y2023.S0101?..."
    ... )
    
    >>> # Different year
    >>> citation = format_source_citation(
    ...     "S1810",
    ...     "https://data.census.gov/table/...",
    ...     data_year=2020
    ... )
    
    >>> # Custom citation (for non-Census sources)
    >>> citation = format_source_citation(
    ...     "",
    ...     "",
    ...     custom_text="New York State Department of Health, [Data Source](https://...), 2025"
    ... )
    """
    if custom_text:
        return custom_text
    
    return f'US Census Bureau; American Community Survey, {data_year} American Community Survey {estimate_type}, [Table {table_id}]({url}), {citation_month} {citation_year}'


def create_source_callout(table_id=None, url=None, data_year=2023, estimate_type="5-Year Estimates", citation_month="April", citation_year=2025, custom_text=None):
    """
    Create a complete collapsible source callout box in Quarto format.
    
    This is the STANDARD format for all CHA table sources.
    Flexible to handle different sources from the CHA document.
    
    Parameters
    ----------
    table_id : str, optional
        The Census Bureau table ID (e.g., "S0101", "B03002", "S1601")
        Required if custom_text is not provided
    url : str, optional
        The full URL to the data source
        Required if custom_text is not provided
    data_year : int, optional
        The data year (default: 2023)
    estimate_type : str, optional
        The estimate type - "5-Year Estimates" or "5-year estimates" (default: "5-Year Estimates")
    citation_month : str, optional
        The citation month (default: "April")
    citation_year : int, optional
        The citation year (default: 2025)
    custom_text : str, optional
        Custom citation text for non-Census sources or special cases.
        Should include hyperlinks in markdown format: [text](url)
        If provided, other parameters are ignored.
        
    Returns
    -------
    str
        Complete Quarto callout block for source citation
        
    Examples
    --------
    >>> # Standard Census Bureau table
    >>> callout = create_source_callout(
    ...     "S0101",
    ...     "https://data.census.gov/table/ACSST5Y2023.S0101?..."
    ... )
    
    >>> # Different year (2020 data)
    >>> callout = create_source_callout(
    ...     "S1810",
    ...     "https://data.census.gov/table/...",
    ...     data_year=2020
    ... )
    
    >>> # Custom source (e.g., NYS Department of Health)
    >>> callout = create_source_callout(
    ...     custom_text="New York State Department of Health, [Vital Statistics](https://...), 2025"
    ... )
    """
    citation = format_source_citation(
        table_id or "", 
        url or "", 
        data_year, 
        estimate_type, 
        citation_month, 
        citation_year,
        custom_text
    )
    return f'''::: {{.callout-note collapse="true"}}
## Source

{citation}
:::'''


# Standard source citation format
STANDARD_SOURCE_FORMAT = """::: {.callout-note collapse="true"}
## Source

US Census Bureau; American Community Survey, {year} American Community Survey 5-Year Estimates, [Table {table_id}]({url}), {month} {citation_year}
:::"""

# Template for Quarto table code block
QUARTO_TABLE_TEMPLATE = '''```{{python}}
#| echo: false
#| warning: false
#| message: false
#| label: tbl-{table_label}
#| tbl-cap: "{table_caption}"
import pandas as pd
import numpy as np
from scripts.cha_table_styling import style_cha_table

# Create the data
data = {{
    # Your data dictionary here
}}

df = pd.DataFrame(data)

# Format the data (adjust as needed)
# df["Column Name"] = df["Column Name"].apply(lambda x: f"{{x:,}}")
# df["Percent Column"] = df["Percent Column"].apply(lambda x: f"{{x:.1f}}" if pd.notna(x) else "N/A")

# Apply standard CHA styling
styled_table = style_cha_table(df)
styled_table
```

{source_callout}
'''

