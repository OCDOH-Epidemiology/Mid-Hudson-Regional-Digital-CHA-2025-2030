"""
CHA Figure Builder

Utilities for creating CHA figures (lines, clustered bars, stacked bars)
with consistent styling and ordering. Includes a helper to display a
figure above its table output in Quarto/Jupyter.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from scripts.cha_table_styling import (
    CHA_REGION_ALIASES,
    CHA_REGION_ORDER,
    style_cha_table,
)


CHA_COLOR_PALETTE = [
    "#9ACD4B",
    "#FAA83B",
    "#D35840",
    "#9941B1",
    "#63A0CC",
    "#82FFFF",
    "#5E8425",
    "#EBE603",
    "#D91AC4",
    "#18AC93",
]

DEFAULT_DASHED_SERIES = {"NYS": "dash", "US": "dash"}


def _normalize_label(label: str) -> str:
    normalized = str(label).strip()
    return CHA_REGION_ALIASES.get(normalized, normalized)


def _ordered_series(series: list[str]) -> list[str]:
    normalized = {name: _normalize_label(name) for name in series}
    ordered = [name for name in series if normalized[name] in CHA_REGION_ORDER]
    ordered.sort(key=lambda name: CHA_REGION_ORDER.index(normalized[name]))
    remaining = [name for name in series if name not in ordered]
    return ordered + remaining


def _series_colors(series: list[str], palette: list[str] | None = None) -> dict[str, str]:
    palette = palette or CHA_COLOR_PALETTE
    return {name: palette[idx % len(palette)] for idx, name in enumerate(series)}


def _series_dashes(series: list[str], overrides: dict[str, str] | None = None) -> dict[str, str]:
    dashes = {name: "solid" for name in series}
    for name, style in (overrides or DEFAULT_DASHED_SERIES).items():
        if name in dashes:
            dashes[name] = style
    return dashes


def _round_up_to_nice_number(value: float) -> float:
    """
    Round up to the next nice round number.
    Examples: 92 -> 100, 150 -> 200, 250 -> 300, 850 -> 900, 950 -> 1000
    """
    if value <= 0:
        return 100.0
    if value <= 100:
        return 100.0
    
    # For values > 100, round up to the next 100
    return ((int(value) // 100) + 1) * 100


def _y_range(values: pd.Series, start_at_zero: bool, padding: float, is_bar_graph: bool = False) -> list[float]:
    y_min = float(values.min())
    y_max = float(values.max())
    
    # Use original logic for all graph types (bar graphs and line graphs)
    if start_at_zero:
        y_min = 0.0
    y_span = y_max - y_min
    if y_span == 0:
        y_span = 1.0
    return [y_min - y_span * padding, y_max + y_span * padding]


def _apply_layout(
    fig: go.Figure,
    x_axis_title: str,
    y_axis_title: str,
    y_range: list[float] | None,
    width: int,
    height: int,
    font_family: str,
    is_bar_graph: bool = False,
) -> None:
    yaxis_dict = dict(
        title=dict(text=y_axis_title, font=dict(size=14, family=font_family)),
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
        gridwidth=1,
    )
    
    if y_range:
        yaxis_dict["range"] = y_range
        if is_bar_graph:
            # For bar graphs, disable autorange to ensure the range stays fixed
            yaxis_dict["autorange"] = False
    
    fig.update_layout(
        xaxis=dict(
            title=dict(text=x_axis_title, font=dict(size=14, family=font_family)),
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.2)",
            gridwidth=1,
        ),
        yaxis=yaxis_dict,
        hovermode="x unified",
        legend=dict(
            x=1.02,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            font=dict(size=11),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1,
        ),
        plot_bgcolor="white",
        width=width,
        height=height,
        margin=dict(l=80, r=200, t=40, b=60),
    )


def build_line_figure(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str] | None = None,
    *,
    x_axis_title: str | None = None,
    y_axis_title: str,
    start_at_zero: bool = False,
    y_padding: float = 0.1,
    palette: list[str] | None = None,
    dash_overrides: dict[str, str] | None = None,
    width: int = 1000,
    height: int = 600,
    font_family: str = "Arial, sans-serif",
    hover_value_format: str = ".1f",
    hover_suffix: str = "",
) -> go.Figure:
    series = y_cols or [col for col in df.columns if col != x_col]
    ordered = _ordered_series(series)
    colors = _series_colors(ordered, palette)
    dashes = _series_dashes(ordered, dash_overrides)
    x_axis_title = x_axis_title or x_col
    value_label = y_axis_title or "Value"

    fig = go.Figure()
    for col in ordered:
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="lines+markers",
                name=col,
                line=dict(
                    color=colors[col],
                    width=3 if col in ["NYS", "US"] else 2.5,
                    dash=dashes[col],
                ),
                marker=dict(size=8, color=colors[col], line=dict(width=1.5, color="white")),
                hovertemplate=(
                    f"<b>{col}</b><br>{x_axis_title}: %{{x}}<br>"
                    f"{value_label}: %{{y:{hover_value_format}}}{hover_suffix}"
                    "<extra></extra>"
                ),
            )
        )

    y_values = df[ordered].to_numpy().flatten()
    y_range = _y_range(pd.Series(y_values), start_at_zero, y_padding)
    _apply_layout(
        fig=fig,
        x_axis_title=x_axis_title,
        y_axis_title=y_axis_title,
        y_range=y_range,
        width=width,
        height=height,
        font_family=font_family,
    )
    return fig


def build_clustered_bar_figure(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str] | None = None,
    *,
    x_axis_title: str | None = None,
    y_axis_title: str,
    start_at_zero: bool = True,
    y_padding: float = 0.1,
    palette: list[str] | None = None,
    width: int = 1000,
    height: int = 600,
    font_family: str = "Arial, sans-serif",
    hover_value_format: str = ".1f",
    hover_suffix: str = "",
) -> go.Figure:
    series = y_cols or [col for col in df.columns if col != x_col]
    ordered = _ordered_series(series)
    colors = _series_colors(ordered, palette)
    x_axis_title = x_axis_title or x_col
    value_label = y_axis_title or "Value"

    fig = go.Figure()
    for col in ordered:
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[col],
                name=col,
                marker=dict(color=colors[col]),
                hovertemplate=(
                    f"<b>{col}</b><br>{x_axis_title}: %{{x}}<br>"
                    f"{value_label}: %{{y:{hover_value_format}}}{hover_suffix}"
                    "<extra></extra>"
                ),
            )
        )

    y_values = df[ordered].to_numpy().flatten()
    y_range = _y_range(pd.Series(y_values), start_at_zero, y_padding, is_bar_graph=True)
    _apply_layout(
        fig=fig,
        x_axis_title=x_axis_title,
        y_axis_title=y_axis_title,
        y_range=y_range,
        width=width,
        height=height,
        font_family=font_family,
        is_bar_graph=True,
    )
    fig.update_layout(barmode="group")
    return fig


def build_stacked_bar_figure(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str] | None = None,
    *,
    x_axis_title: str | None = None,
    y_axis_title: str,
    start_at_zero: bool = True,
    y_padding: float = 0.1,
    palette: list[str] | None = None,
    width: int = 1000,
    height: int = 600,
    font_family: str = "Arial, sans-serif",
    hover_value_format: str = ".1f",
    hover_suffix: str = "",
) -> go.Figure:
    series = y_cols or [col for col in df.columns if col != x_col]
    ordered = _ordered_series(series)
    colors = _series_colors(ordered, palette)
    x_axis_title = x_axis_title or x_col
    value_label = y_axis_title or "Value"

    fig = go.Figure()
    for col in ordered:
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[col],
                name=col,
                marker=dict(color=colors[col]),
                hovertemplate=(
                    f"<b>{col}</b><br>{x_axis_title}: %{{x}}<br>"
                    f"{value_label}: %{{y:{hover_value_format}}}{hover_suffix}"
                    "<extra></extra>"
                ),
            )
        )

    totals = df[ordered].sum(axis=1)
    y_range = _y_range(pd.Series(totals), start_at_zero, y_padding, is_bar_graph=True)
    _apply_layout(
        fig=fig,
        x_axis_title=x_axis_title,
        y_axis_title=y_axis_title,
        y_range=y_range,
        width=width,
        height=height,
        font_family=font_family,
        is_bar_graph=True,
    )
    fig.update_layout(barmode="stack")
    return fig


def build_interactive_line_figure(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str] | None = None,
    *,
    x_axis_title: str | None = None,
    y_axis_title: str,
    start_at_zero: bool = False,
    y_padding: float = 0.1,
    palette: list[str] | None = None,
    dash_overrides: dict[str, str] | None = None,
    width: int = 1000,
    height: int = 600,
    font_family: str = "Arial, sans-serif",
    hover_value_format: str = ".1f",
    hover_suffix: str = "",
) -> go.Figure:
    """
    Build an interactive line figure with dropdown controls to:
    - Filter counties to compare specific ones
    - Switch between time series view (all years) and single year comparison (bar chart)
    
    This creates a Plotly figure with updatemenus that works directly in Quarto.
    """
    series = y_cols or [col for col in df.columns if col != x_col]
    ordered = _ordered_series(series)
    colors = _series_colors(ordered, palette)
    dashes = _series_dashes(ordered, dash_overrides)
    x_axis_title = x_axis_title or x_col
    value_label = y_axis_title or "Value"
    
    # Get unique years for single-year comparison
    years = sorted(df[x_col].unique().tolist())
    
    # Create base figure with all data (time series view)
    fig = go.Figure()
    
    # Add all traces for time series view
    for col in ordered:
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="lines+markers",
                name=col,
                visible=True,  # All visible by default
                line=dict(
                    color=colors[col],
                    width=3 if col in ["NYS", "US"] else 2.5,
                    dash=dashes[col],
                ),
                marker=dict(size=8, color=colors[col], line=dict(width=1.5, color="white")),
                hovertemplate=(
                    f"<b>{col}</b><br>{x_axis_title}: %{{x}}<br>"
                    f"{value_label}: %{{y:{hover_value_format}}}{hover_suffix}"
                    "<extra></extra>"
                ),
            )
        )
    
    # Add bar chart traces for each year (initially hidden)
    # For each year, create one trace per county - each trace represents one county's bar
    for year in years:
        year_data = df[df[x_col] == year]
        for idx, col in enumerate(ordered):
            value = year_data[col].iloc[0] if len(year_data) > 0 and col in year_data.columns else 0
            # Create a trace with x=[col] so bars group by county name when all are visible
            fig.add_trace(
                go.Bar(
                    x=[col],  # County name on x-axis
                    y=[value],
                    name=col,
                    visible=False,  # Hidden by default
                    marker=dict(color=colors[col]),
                    hovertemplate=(
                        f"<b>{col}</b><br>{x_axis_title}: {year}<br>"
                        f"{value_label}: %{{y:{hover_value_format}}}{hover_suffix}"
                        "<extra></extra>"
                    ),
                    showlegend=True,  # Show legend for bar charts
                    legendgroup=f"{col}_{year}",  # Unique group per year
                )
            )
    
    # Calculate y range
    y_values = df[ordered].to_numpy().flatten()
    y_range = _y_range(pd.Series(y_values), start_at_zero, y_padding)
    
    # Create updatemenus for view switching
    buttons = []
    
    # Time series view button (all counties, all years)
    buttons.append(
        dict(
            label="Time Series (All Years)",
            method="update",
            args=[
                {
                    "visible": [True] * len(ordered) + [False] * (len(ordered) * len(years)),
                },
                {
                    "xaxis": {"title": x_axis_title},
                    "barmode": None,
                },
            ],
        )
    )
    
    # Single year comparison buttons (bar charts)
    for year in years:
        year_idx = years.index(year)
        # Show bar traces for this year, hide line traces
        visibility = [False] * len(ordered) + [False] * (len(ordered) * len(years))
        for i, col in enumerate(ordered):
            trace_idx = len(ordered) + (year_idx * len(ordered)) + i
            visibility[trace_idx] = True
        
        buttons.append(
            dict(
                label=f"Compare by Year ({year})",
                method="update",
                args=[
                    {"visible": visibility},
                    {
                        "xaxis": {"title": "County"},
                        "barmode": "group",
                    },
                ],
            )
        )
    
    # Create dropdown for county filtering (only applies to time series view)
    county_buttons = []
    county_buttons.append(
        dict(
            label="All Counties",
            method="restyle",
            args=[{"visible": [True] * len(ordered)}],
        )
    )
    
    # Add buttons for individual counties
    for col in ordered:
        visibility = [False] * len(ordered)
        visibility[ordered.index(col)] = True
        county_buttons.append(
            dict(
                label=col,
                method="restyle",
                args=[{"visible": visibility}],
            )
        )
    
    # Add buttons for county groups
    county_groups = {
        "Mid-Hudson Counties": [c for c in ordered if c not in ["NYS", "US"]],
        "Counties Only": [c for c in ordered if c not in ["NYS", "US"]],
        "With Benchmarks": ordered,
    }
    
    for group_name, group_counties in county_groups.items():
        visibility = [c in group_counties for c in ordered]
        county_buttons.append(
            dict(
                label=group_name,
                method="restyle",
                args=[{"visible": visibility}],
            )
        )
    
    # Apply layout
    _apply_layout(
        fig=fig,
        x_axis_title=x_axis_title,
        y_axis_title=y_axis_title,
        y_range=y_range,
        width=width,
        height=height,
        font_family=font_family,
    )
    
    # Add updatemenus
    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                showactive=True,
                x=0.02,
                xanchor="left",
                y=1.02,
                yanchor="top",
                buttons=buttons,
                pad={"r": 10, "t": 10},
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1,
            ),
            dict(
                type="dropdown",
                direction="down",
                showactive=True,
                x=0.25,
                xanchor="left",
                y=1.02,
                yanchor="top",
                buttons=county_buttons,
                pad={"r": 10, "t": 10},
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1,
            ),
        ],
        annotations=[
            dict(
                text="View:",
                x=0.02,
                xref="paper",
                y=1.08,
                yref="paper",
                align="left",
                showarrow=False,
                font=dict(size=12),
            ),
            dict(
                text="Filter Counties:",
                x=0.25,
                xref="paper",
                y=1.08,
                yref="paper",
                align="left",
                showarrow=False,
                font=dict(size=12),
            ),
        ],
    )
    
    return fig


def render_figure_and_table(
    fig: go.Figure,
    df: pd.DataFrame,
    *,
    has_multilevel_headers: bool = False,
) -> None:
    """
    Display a figure above its table in Quarto/Jupyter output.
    Use chunk options for figure and table captions/labels.
    """
    from IPython.display import display

    fig.show()
    styled_table = style_cha_table(df, has_multilevel_headers=has_multilevel_headers)
    display(styled_table)
