"""Report & export page: PDF report and clean-dataset exports (Modules 7-9)."""

from __future__ import annotations

import streamlit as st

from utils import analyzer, exporter
from utils.helpers import format_number, load_history


def _require_dataframe():
    """Return the active DataFrame or display a warning and return ``None``."""
    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a file on the Dashboard page first.")
        return None
    return df


def render() -> None:
    """Render the report, export and history page."""
    st.markdown("## 📄 Report & Export")

    df = _require_dataframe()
    if df is None:
        return

    info = st.session_state.get("file_info")
    filename = info.name if info else "dataset"

    # Recompute analysis fresh so the report reflects the current (cleaned) data.
    quality = analyzer.quality_report(df)
    stats = analyzer.numeric_statistics(df)
    insight = analyzer.analyze_dataset(df)

    kpis = {
        "Total rows": format_number(df.shape[0]),
        "Total columns": format_number(df.shape[1]),
        "Missing values": format_number(quality["missing_total"]),
        "Missing %": f"{quality['missing_percentage']}%",
        "Duplicates": format_number(quality["duplicates"]),
    }

    # --- Exports ---
    st.markdown("### Export cleaned dataset")
    col1, col2, col3 = st.columns(3)
    col1.download_button(
        "⬇️ Excel (.xlsx)",
        data=exporter.to_excel_bytes(df),
        file_name="cleaned_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    col2.download_button(
        "⬇️ CSV (.csv)",
        data=exporter.to_csv_bytes(df),
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )
    pdf_bytes = exporter.build_pdf_report(filename, kpis, stats, insight)
    col3.download_button(
        "⬇️ PDF report",
        data=pdf_bytes,
        file_name="analysis_report.pdf",
        mime="application/pdf",
    )

    # --- Report preview ---
    st.markdown("### Report content preview")
    st.success(insight.summary)
    st.json(kpis)

    # --- History (Module 9) ---
    st.markdown("### 🕓 Analysis history")
    history = load_history()
    if not history:
        st.info("No analyses recorded yet.")
    else:
        st.dataframe(history, use_container_width=True)
