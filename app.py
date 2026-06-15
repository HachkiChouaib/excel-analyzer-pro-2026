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

from pages import analysis, cleaning, dashboard, login, report, visualization
from utils import theme
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


def apply_styles() -> None:
    """Inject the dynamic theme palette followed by the structural stylesheet.

    Order matters: theme variables are defined first, then ``styles.css``
    (which references those variables) is applied on top.
    """
    mode = st.session_state.get("theme", "light")
    css = theme.build_css(mode)
    if CSS_FILE.exists():
        css += CSS_FILE.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def theme_toggle(key: str) -> None:
    """Render a light/dark theme switch bound to session state.

    Args:
        key: Unique Streamlit widget key (a screen may render several).
    """
    is_dark = st.session_state.get("theme", "light") == "dark"
    new_dark = st.toggle("🌙 Dark mode", value=is_dark, key=key)
    new_mode = "dark" if new_dark else "light"
    if new_mode != st.session_state.get("theme", "light"):
        st.session_state["theme"] = new_mode
        st.rerun()


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
        # Functional light/dark switch (re-applies the palette on change).
        theme_toggle(key="theme_toggle_sidebar")

        if st.session_state.get("file_info"):
            info = st.session_state["file_info"]
            st.success(f"Loaded: {info.name}\n\n{info.rows:,} rows × {info.columns} cols")

        # --- Logged-in user panel ---
        st.divider()
        st.caption(f"👤 Signed in as **{st.session_state['user']}**")
        if st.button("Log out", use_container_width=True):
            # Clear session-scoped state on logout.
            for key in ("user", "df", "file_info", "insight"):
                st.session_state.pop(key, None)
            st.rerun()

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
    # Default theme on first load.
    st.session_state.setdefault("theme", "light")
    apply_styles()

    # --- Authentication gate (portfolio bonus) ---
    if not login.render():
        return

    selected = render_sidebar()
    # Dispatch to the selected page's render function.
    _, render_func = PAGES[selected]
    render_func()


if __name__ == "__main__":
    main()
