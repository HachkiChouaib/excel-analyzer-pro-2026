"""Excel Analyzer Pro 2026 - main Streamlit entry point.

Responsibilities:
    * Configure the page and inject custom CSS.
    * Build a professional sidebar with custom navigation.
    * Route to the selected page module's ``render()`` function.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from pages import analysis, cleaning, dashboard, report, visualization
from utils.helpers import ensure_directories

# --- Static paths ---------------------------------------------------------
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
CSS_FILE = ASSETS_DIR / "styles.css"

# --- Navigation registry: label -> (icon, render function) ----------------
PAGES: dict[str, tuple[str, object]] = {
    "Dashboard": ("📊", dashboard.render),
    "Analysis": ("🔍", analysis.render),
    "Cleaning": ("🧹", cleaning.render),
    "Visualization": ("📈", visualization.render),
    "Report & Export": ("📄", report.render),
}


def load_css() -> None:
    """Inject the custom stylesheet, if present."""
    if CSS_FILE.exists():
        st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
                    unsafe_allow_html=True)


def render_sidebar() -> str:
    """Render the sidebar navigation and theme toggle.

    Returns:
        The label of the currently selected page.
    """
    with st.sidebar:
        st.markdown("<div class='app-brand'>📊 Excel Analyzer Pro</div>",
                    unsafe_allow_html=True)
        st.markdown("<div class='app-tagline'>Analyze · Clean · Visualize · Report</div>",
                    unsafe_allow_html=True)
        st.divider()

        # Custom navigation (replaces Streamlit's auto multipage nav).
        choice = st.radio(
            "Navigation",
            options=list(PAGES.keys()),
            format_func=lambda label: f"{PAGES[label][0]}  {label}",
            label_visibility="collapsed",
        )

        st.divider()
        # Theme toggle is informational here; the active palette is set in
        # config.toml. Streamlit's built-in Settings menu switches light/dark.
        st.caption("Tip: use the ☰ menu → Settings to switch light/dark theme.")

        if st.session_state.get("file_info"):
            info = st.session_state["file_info"]
            st.success(f"Loaded: {info.name}\n\n{info.rows:,} rows × {info.columns} cols")

    return choice


def main() -> None:
    """Application bootstrap and router."""
    st.set_page_config(
        page_title="Excel Analyzer Pro 2026",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    ensure_directories()
    load_css()

    selected = render_sidebar()
    # Dispatch to the selected page's render function.
    _, render_func = PAGES[selected]
    render_func()


if __name__ == "__main__":
    main()
