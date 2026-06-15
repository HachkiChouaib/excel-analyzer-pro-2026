"""Dashboard page: upload area, file info and KPI cards (Modules 1 & 4)."""

from __future__ import annotations

import streamlit as st

from utils import analyzer, file_handler
from utils.helpers import append_history, format_number


def _kpi_card(label: str, value: str, icon: str) -> str:
    """Return the HTML markup for a single KPI card."""
    return (
        f"<div class='kpi-card'>"
        f"<div class='kpi-icon'>{icon}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"<div class='kpi-label'>{label}</div>"
        f"</div>"
    )


def _handle_upload(uploaded_file) -> None:
    """Read an uploaded file into session state and record history."""
    if not file_handler.is_supported(uploaded_file.name):
        st.error("Unsupported file type. Please upload a .xlsx, .xls or .csv file.")
        return
    try:
        df = file_handler.read_file(uploaded_file, uploaded_file.name)
    except ValueError as exc:
        st.error(f"Could not read the file: {exc}")
        return

    info = file_handler.build_file_info(df, uploaded_file.name, uploaded_file.size)
    # Persist both the original and the working (cleanable) copy.
    st.session_state["df"] = df
    st.session_state["file_info"] = info
    append_history(info.name, info.rows, info.columns)
    st.success(f"Loaded '{info.name}' successfully.")


def render() -> None:
    """Render the dashboard page."""
    st.markdown("## 📊 Dashboard")

    uploaded_file = st.file_uploader(
        "Import an Excel or CSV file",
        type=["xlsx", "xls", "csv"],
        help="Drag and drop your dataset here.",
    )
    if uploaded_file is not None:
        _handle_upload(uploaded_file)

    df = st.session_state.get("df")
    info = st.session_state.get("file_info")
    if df is None or info is None:
        st.info("👆 Upload a file to get started.")
        return

    # --- File information ---
    st.markdown("### File information")
    cols = st.columns(4)
    cols[0].metric("Name", info.name)
    cols[1].metric("Size", info.size_label)
    cols[2].metric("Rows", format_number(info.rows))
    cols[3].metric("Columns", format_number(info.columns))

    # --- KPI cards (Power BI style) ---
    quality = analyzer.quality_report(df)
    st.markdown("### Key indicators")
    cards = "".join(
        [
            _kpi_card("Total rows", format_number(info.rows), "📈"),
            _kpi_card("Total columns", format_number(info.columns), "🧮"),
            _kpi_card("Missing values", format_number(quality["missing_total"]), "⚠️"),
            _kpi_card("Duplicates", format_number(quality["duplicates"]), "🔁"),
        ]
    )
    st.markdown(f"<div class='kpi-grid'>{cards}</div>", unsafe_allow_html=True)

    # --- Data preview ---
    st.markdown("### Data preview")
    st.dataframe(df.head(50), use_container_width=True)
