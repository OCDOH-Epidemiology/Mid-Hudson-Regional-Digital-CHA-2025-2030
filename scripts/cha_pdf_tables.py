"""
PDF-specific table rendering helpers for Quarto/Jupyter output.
"""

from __future__ import annotations

import os
from typing import Literal

import pandas as pd

TablePolicy = Literal["fit", "split"]

DEFAULT_TABLE_POLICY: TablePolicy = "fit"

# Per-table behavior overrides. Keep this map small and explicit.
TABLE_POLICY_OVERRIDES: dict[str, TablePolicy] = {
    "tbl-population-demographics": "split",
    "tbl-age": "split",
    "tbl-race": "split",
    "tbl-income": "split",
}


def is_pdf_render() -> bool:
    """True when Quarto is currently executing for PDF output."""
    candidates = (
        os.environ.get("QUARTO_FORMAT"),
        os.environ.get("QUARTO_EXECUTE_INFO"),
    )
    for raw in candidates:
        if raw and "pdf" in raw.lower():
            return True
    return False


def resolve_table_policy(table_id: str) -> TablePolicy:
    """Resolve policy from explicit overrides and known-wide naming."""
    if table_id in TABLE_POLICY_OVERRIDES:
        return TABLE_POLICY_OVERRIDES[table_id]
    # Most race/ethnicity breakdown tables are wide.
    if "-rande-" in table_id or table_id.endswith("-rande"):
        return "split"
    return DEFAULT_TABLE_POLICY


def _flatten_columns_for_pdf(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        flattened: list[str] = []
        for parts in out.columns.to_flat_index():
            labels = [str(part).strip() for part in parts if str(part).strip() and str(part).strip() != "."]
            flattened.append(" / ".join(labels) if labels else "")
        out.columns = flattened
    else:
        out.columns = [str(col) for col in out.columns]
    return out


def _df_to_longtable_latex(df: pd.DataFrame) -> str:
    return df.to_latex(
        index=False,
        na_rep="",
        longtable=True,
        escape=True,
    )


def _df_to_fit_latex(df: pd.DataFrame) -> str:
    tabular = df.to_latex(
        index=False,
        na_rep="",
        longtable=False,
        escape=True,
    )
    return "\n".join(
        [
            r"\begingroup",
            r"\setlength{\tabcolsep}{4pt}",
            r"\renewcommand{\arraystretch}{1.1}",
            r"\resizebox{\linewidth}{!}{%",
            tabular,
            r"}",
            r"\endgroup",
        ]
    )


def _split_wide_columns(df: pd.DataFrame, max_columns_per_part: int = 6) -> list[pd.DataFrame]:
    if len(df.columns) <= max_columns_per_part:
        return [df]
    first_col = df.columns[0]
    trailing = list(df.columns[1:])
    chunk_size = max(1, max_columns_per_part - 1)
    parts: list[pd.DataFrame] = []
    for idx in range(0, len(trailing), chunk_size):
        subset = [first_col] + trailing[idx : idx + chunk_size]
        parts.append(df[subset].copy())
    return parts


def render_pdf_table_latex(table_id: str, df: pd.DataFrame) -> str:
    table_df = _flatten_columns_for_pdf(df)
    policy = resolve_table_policy(table_id)

    if policy == "split":
        parts = _split_wide_columns(table_df)
        total = len(parts)
        rendered_parts = []
        for idx, part in enumerate(parts, start=1):
            part_latex = _df_to_longtable_latex(part)
            if total > 1:
                rendered_parts.append(
                    "\n".join(
                        [
                            rf"\textit{{Table continuation ({idx}/{total})}}",
                            r"\vspace{0.3em}",
                            part_latex,
                            r"\vspace{0.8em}",
                        ]
                    )
                )
            else:
                rendered_parts.append(part_latex)
        return "\n".join(rendered_parts)

    return _df_to_fit_latex(table_df)
