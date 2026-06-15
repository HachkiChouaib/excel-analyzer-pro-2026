"""Visualization page: interactive Plotly charts (Module 5)."""

from __future__ import annotations

import streamlit as st

from utils import analyzer, charts
from utils.helpers import classify_columns


def _require_dataframe():
    """Return the active DataFrame or display a warning and return ``None``."""
    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a file on the Dashboard page first.")
        return None
    return df


def render() -> None:
    """Render the visualization page."""
    st.markdown("## 📈 Visualizations")

    df = _require_dataframe()
    if df is None:
        return

    groups = classify_columns(df)
    numeric, text = groups["numeric"], groups["text"]

    chart_type = st.selectbox(
        "Chart type",
        options=["Histogram", "Pie chart", "Bar chart", "Scatter plot", "Heatmap"],
    )

    if chart_type == "Histogram":
        if not numeric:
            st.info("No numeric columns available.")
            return
        column = st.selectbox("Column", options=numeric)
        bins = st.slider("Bins", min_value=5, max_value=100, value=30)
        st.plotly_chart(charts.histogram(df, column, bins), use_container_width=True)

    elif chart_type == "Pie chart":
        candidates = text or list(df.columns)
        column = st.selectbox("Category column", options=candidates)
        st.plotly_chart(charts.pie_chart(df, column), use_container_width=True)

    elif chart_type == "Bar chart":
        if not numeric:
            st.info("No numeric columns available.")
            return
        x = st.selectbox("X (category)", options=list(df.columns))
        y = st.selectbox("Y (value)", options=numeric)
        st.plotly_chart(charts.bar_chart(df, x, y), use_container_width=True)

    elif chart_type == "Scatter plot":
        if len(numeric) < 2:
            st.info("Need at least two numeric columns.")
            return
        x = st.selectbox("X axis", options=numeric, key="scatter_x")
        y = st.selectbox("Y axis", options=numeric, index=1, key="scatter_y")
        st.plotly_chart(charts.scatter_plot(df, x, y), use_container_width=True)

    elif chart_type == "Heatmap":
        corr = analyzer.correlation_matrix(df)
        if corr.empty:
            st.info("Need at least two numeric columns for a correlation heatmap.")
            return
        st.plotly_chart(charts.heatmap(corr), use_container_width=True)
