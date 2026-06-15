"""Cleaning page: interactive data-cleaning operations (Module 3)."""

from __future__ import annotations

import streamlit as st

from utils import cleaner


def _require_dataframe():
    """Return the active DataFrame or display a warning and return ``None``."""
    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a file on the Dashboard page first.")
        return None
    return df


def render() -> None:
    """Render the data-cleaning page."""
    st.markdown("## 🧹 Data Cleaning")

    df = _require_dataframe()
    if df is None:
        return

    st.caption(f"Current shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

    # --- Remove duplicates ---
    st.markdown("### Remove duplicates")
    if st.button("Remove duplicate rows"):
        st.session_state["df"] = cleaner.remove_duplicates(df)
        st.success("Duplicates removed.")
        st.rerun()

    # --- Missing values ---
    st.markdown("### Handle missing values")
    strategy = st.selectbox(
        "Strategy",
        options=["drop", "mean", "median", "zero"],
        format_func=lambda s: {
            "drop": "Drop rows with missing values",
            "mean": "Replace with column mean",
            "median": "Replace with column median",
            "zero": "Replace with zero",
        }[s],
    )
    if st.button("Apply missing-value strategy"):
        st.session_state["df"] = cleaner.handle_missing(df, strategy)
        st.success(f"Applied strategy: {strategy}.")
        st.rerun()

    # --- Rename a column ---
    st.markdown("### Rename a column")
    col_to_rename = st.selectbox("Column", options=list(df.columns), key="rename_col")
    new_name = st.text_input("New name", value=col_to_rename)
    if st.button("Rename column") and new_name.strip():
        st.session_state["df"] = cleaner.rename_columns(df, {col_to_rename: new_name})
        st.success(f"Renamed '{col_to_rename}' to '{new_name}'.")
        st.rerun()

    # --- Convert a column type ---
    st.markdown("### Convert column type")
    conv_col = st.selectbox("Column to convert", options=list(df.columns), key="conv_col")
    target = st.radio("Target type", options=["text", "number", "date"], horizontal=True)
    if st.button("Convert type"):
        st.session_state["df"] = cleaner.convert_column(df, conv_col, target)
        st.success(f"Converted '{conv_col}' to {target}.")
        st.rerun()

    # --- Preview ---
    st.markdown("### Preview")
    st.dataframe(st.session_state["df"].head(50), use_container_width=True)
