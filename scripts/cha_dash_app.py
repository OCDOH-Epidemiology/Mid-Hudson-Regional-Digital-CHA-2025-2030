"""
Dash App for CHA Interactive Figures

A standalone Dash application for comparing counties across years.
Run with: python scripts/cha_dash_app.py

Then access at http://localhost:8050
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from scripts.cha_figure_builder import (
    CHA_COLOR_PALETTE,
    _ordered_series,
    _series_colors,
    _series_dashes,
    DEFAULT_DASHED_SERIES,
)


def create_sample_data():
    """Create sample labor force data"""
    return {
        "Year": [2021, 2022, 2023],
        "Dutchess": [63.0, 62.8, 63.3],
        "Orange": [63.9, 63.4, 63.5],
        "Putnam": [65.2, 64.7, 64.7],
        "Rockland": [63.9, 63.2, 63.2],
        "Sullivan": [56.1, 58.1, 59.1],
        "Ulster": [60.1, 58.9, 58.7],
        "Westchester": [65.5, 65.2, 65.4],
        "NYS": [63.1, 62.9, 63.0],
        "US": [63.6, 63.5, 63.5],
    }


# Initialize Dash app
app = dash.Dash(__name__)

# Sample data - in production, load from your data source
df = pd.DataFrame(create_sample_data())

# Get counties (excluding Year column)
counties = [col for col in df.columns if col != "Year"]
ordered_counties = _ordered_series(counties)
colors = _series_colors(ordered_counties)
dashes = _series_dashes(ordered_counties, DEFAULT_DASHED_SERIES)
years = sorted(df["Year"].unique().tolist())

# App layout
app.layout = html.Div(
    [
        html.H1("Mid-Hudson Regional CHA - Interactive County Comparison", style={"textAlign": "center"}),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("View Type:", style={"fontWeight": "bold", "marginBottom": "5px"}),
                        dcc.RadioItems(
                            id="view-type",
                            options=[
                                {"label": "Time Series (All Years)", "value": "timeseries"},
                                {"label": "Single Year Comparison", "value": "single-year"},
                            ],
                            value="timeseries",
                            style={"marginBottom": "20px"},
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"},
                ),
                html.Div(
                    [
                        html.Label("Select Year:", style={"fontWeight": "bold", "marginBottom": "5px"}),
                        dcc.Dropdown(
                            id="year-selector",
                            options=[{"label": str(year), "value": year} for year in years],
                            value=years[-1],
                            style={"marginBottom": "20px"},
                            disabled=False,
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"},
                ),
                html.Div(
                    [
                        html.Label("Select Counties:", style={"fontWeight": "bold", "marginBottom": "5px"}),
                        dcc.Checklist(
                            id="county-selector",
                            options=[{"label": county, "value": county} for county in ordered_counties],
                            value=ordered_counties,  # All selected by default
                            style={"maxHeight": "300px", "overflowY": "auto"},
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"},
                ),
            ],
            style={"display": "flex", "justifyContent": "space-around", "marginBottom": "30px"},
        ),
        dcc.Graph(id="comparison-graph", style={"height": "600px"}),
        html.Div(
            [
                html.H3("Instructions:", style={"marginTop": "30px"}),
                html.Ul(
                    [
                        html.Li("Select 'Time Series' to view trends across all years"),
                        html.Li("Select 'Single Year Comparison' to compare counties for a specific year"),
                        html.Li("Use the year dropdown to select which year to compare (only applies to single year view)"),
                        html.Li("Check/uncheck counties to filter which ones are displayed"),
                    ]
                ),
            ],
            style={"marginTop": "30px", "padding": "20px", "backgroundColor": "#f0f0f0", "borderRadius": "5px"},
        ),
    ],
    style={"padding": "20px", "fontFamily": "Arial, sans-serif"},
)


@callback(
    Output("comparison-graph", "figure"),
    Output("year-selector", "disabled"),
    Input("view-type", "value"),
    Input("year-selector", "value"),
    Input("county-selector", "value"),
)
def update_graph(view_type, selected_year, selected_counties):
    """Update the graph based on user selections"""
    if not selected_counties:
        # If no counties selected, show empty figure
        return go.Figure().add_annotation(text="Please select at least one county"), False

    # Filter data to selected counties
    filtered_df = df[["Year"] + selected_counties]
    ordered_selected = _ordered_series(selected_counties)

    if view_type == "timeseries":
        # Time series view - line chart
        fig = go.Figure()
        for county in ordered_selected:
            fig.add_trace(
                go.Scatter(
                    x=filtered_df["Year"],
                    y=filtered_df[county],
                    mode="lines+markers",
                    name=county,
                    line=dict(
                        color=colors[county],
                        width=3 if county in ["NYS", "US"] else 2.5,
                        dash=dashes[county],
                    ),
                    marker=dict(size=8, color=colors[county], line=dict(width=1.5, color="white")),
                    hovertemplate=f"<b>{county}</b><br>Year: %{{x}}<br>Value: %{{y:.1f}}%<extra></extra>",
                )
            )

        fig.update_layout(
            title="Percentage of Labor Force Over Time",
            xaxis_title="Year",
            yaxis_title="Percentage of Labor Force (%)",
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
            height=600,
            margin=dict(l=80, r=200, t=60, b=60),
        )
        fig.update_xaxes(tickmode="linear", tick0=years[0], dtick=1)

        return fig, True  # Disable year selector for time series

    else:
        # Single year comparison - bar chart
        year_data = filtered_df[filtered_df["Year"] == selected_year]
        if len(year_data) == 0:
            return go.Figure().add_annotation(text="No data available for selected year"), False

        fig = go.Figure()
        for county in ordered_selected:
            value = year_data[county].iloc[0] if len(year_data) > 0 else 0
            fig.add_trace(
                go.Bar(
                    x=[county],
                    y=[value],
                    name=county,
                    marker=dict(color=colors[county]),
                    hovertemplate=f"<b>{county}</b><br>Year: {selected_year}<br>Value: %{{y:.1f}}%<extra></extra>",
                )
            )

        fig.update_layout(
            title=f"Percentage of Labor Force by County - {selected_year}",
            xaxis_title="County",
            yaxis_title="Percentage of Labor Force (%)",
            barmode="group",
            hovermode="closest",
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
            height=600,
            margin=dict(l=80, r=200, t=60, b=60),
        )

        return fig, False  # Enable year selector for single year view


if __name__ == "__main__":
    print("Starting Dash app...")
    print("Access the app at http://localhost:8050")
    print("Press Ctrl+C to stop the server")
    app.run_server(debug=True, port=8050)
