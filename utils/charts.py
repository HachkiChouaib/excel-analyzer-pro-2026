"""Plotly chart factories.

Each function returns a ``plotly.graph_objects.Figure`` so it can be rendered
in Streamlit *and* exported as a static image inside the PDF report.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Shared colour palette and template for a consistent, professional look.
TEMPLATE: str = "plotly_white"
COLOR_SEQUENCE: list[str] = ["#2563eb", "#7c3aed", "#0891b2", "#16a34a", "#ea580c"]


def _style(fig: go.Figure, title: str) -> go.Figure:
    """Apply the shared layout styling to a figure.

    Args:
        fig: The figure to style.
        title: Chart title.

    Returns:
        The same figure, styled in place (returned for chaining).
    """
    fig.update_layout(
        title=title,
        template=TEMPLATE,
        title_font_size=18,
        margin=dict(l=40, r=20, t=60, b=40),
        colorway=COLOR_SEQUENCE,
    )
    return fig


def histogram(df: pd.DataFrame, column: str, bins: int = 30) -> go.Figure:
    """Build a histogram showing the distribution of a numeric column.

    Args:
        df: Source DataFrame.
        column: Numeric column to plot.
        bins: Number of histogram bins.

    Returns:
        A styled histogram figure.
    """
    fig = px.histogram(df, x=column, nbins=bins)
    return _style(fig, f"Distribution of {column}")


def pie_chart(df: pd.DataFrame, column: str, max_categories: int = 10) -> go.Figure:
    """Build a pie chart of category proportions for a column.

    Only the top ``max_categories`` values are shown; the rest are grouped
    into an "Other" slice to keep the chart readable.

    Args:
        df: Source DataFrame.
        column: Categorical column to plot.
        max_categories: Maximum number of distinct slices before grouping.

    Returns:
        A styled pie chart figure.
    """
    counts = df[column].value_counts()
    if len(counts) > max_categories:
        top = counts.iloc[:max_categories]
        other = counts.iloc[max_categories:].sum()
        counts = pd.concat([top, pd.Series({"Other": other})])
    fig = px.pie(names=counts.index, values=counts.values, hole=0.35)
    return _style(fig, f"Breakdown of {column}")


def bar_chart(df: pd.DataFrame, x: str, y: str) -> go.Figure:
    """Build a bar chart comparing values of ``y`` across ``x`` categories.

    Args:
        df: Source DataFrame.
        x: Category axis column.
        y: Numeric value column.

    Returns:
        A styled bar chart figure.
    """
    fig = px.bar(df, x=x, y=y)
    return _style(fig, f"{y} by {x}")


def scatter_plot(df: pd.DataFrame, x: str, y: str) -> go.Figure:
    """Build a scatter plot to inspect the relationship between two columns.

    Args:
        df: Source DataFrame.
        x: Column for the x-axis.
        y: Column for the y-axis.

    Returns:
        A styled scatter plot figure.
    """
    fig = px.scatter(df, x=x, y=y, trendline="ols" if len(df) > 2 else None)
    return _style(fig, f"{y} vs {x}")


def heatmap(corr: pd.DataFrame) -> go.Figure:
    """Build a correlation heatmap from a correlation matrix.

    Args:
        corr: A square correlation DataFrame (see
            :func:`utils.analyzer.correlation_matrix`).

    Returns:
        A styled heatmap figure.
    """
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
    )
    return _style(fig, "Correlation Matrix")
