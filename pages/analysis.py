"""Analysis page: general info, quality report, statistics and AI insight."""

from __future__ import annotations

import streamlit as st

from utils import analyzer
from utils.helpers import format_number


def _require_dataframe():
    """Return the active DataFrame or display a warning and return ``None``."""
    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a file on the Dashboard page first.")
        return None
    return df


def render() -> None:
    """Render the automatic analysis page (Modules 2 & 6)."""
    st.markdown("## 🔍 Automatic Analysis")

    df = _require_dataframe()
    if df is None:
        return

    info = analyzer.general_info(df)
    quality = analyzer.quality_report(df)

    # --- General information ---
    st.markdown("### General information")
    cols = st.columns(5)
    cols[0].metric("Rows", format_number(info["rows"]))
    cols[1].metric("Columns", format_number(info["columns"]))
    cols[2].metric("Numeric", info["numeric_columns"])
    cols[3].metric("Text", info["text_columns"])
    cols[4].metric("Datetime", info["datetime_columns"])

    # --- Quality ---
    st.markdown("### Data quality")
    cols = st.columns(4)
    cols[0].metric("Missing values", format_number(quality["missing_total"]))
    cols[1].metric("Missing %", f"{quality['missing_percentage']}%")
    cols[2].metric("Duplicates", format_number(quality["duplicates"]))
    cols[3].metric("Empty columns", len(quality["empty_columns"]))

    if quality["missing_by_column"]:
        with st.expander("Missing values by column"):
            st.bar_chart(quality["missing_by_column"])

    # --- Statistics ---
    st.markdown("### Numeric statistics")
    stats = analyzer.numeric_statistics(df)
    if stats.empty:
        st.info("No numeric columns to summarise.")
    else:
        st.dataframe(stats, use_container_width=True)

    # --- AI assessment (Module 6) ---
    st.markdown("###  AI Assessment")
    if st.button("Analyze my data", type="primary"):
        insight = analyzer.analyze_dataset(df)
        st.session_state["insight"] = insight

    insight = st.session_state.get("insight")
    if insight is not None:
        st.success(insight.summary)
        st.markdown("**Detected issues**")
        for item in insight.issues:
            st.markdown(f"- {item}")
        st.markdown("**Recommendations**")
        for item in insight.recommendations:
            st.markdown(f"- {item}")
