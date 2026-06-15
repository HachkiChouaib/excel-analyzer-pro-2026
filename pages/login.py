"""Login / Register screen (Portfolio bonus: authentication).

Renders a centered, responsive auth card with branded hero header. All styling
lives in ``assets/styles.css`` (targeting Streamlit's form/tab containers).
"""

from __future__ import annotations

import streamlit as st

from utils import auth


def _theme_toggle() -> None:
    """Render a compact light/dark switch on the auth screen."""
    is_dark = st.session_state.get("theme", "light") == "dark"
    new_dark = st.toggle("🌙 Dark", value=is_dark, key="theme_toggle_auth")
    new_mode = "dark" if new_dark else "light"
    if new_mode != st.session_state.get("theme", "light"):
        st.session_state["theme"] = new_mode
        st.rerun()


def _hero() -> None:
    """Render the branded hero header above the auth card."""
    st.markdown(
        "<div class='auth-hero'>"
        "<div class='auth-logo-badge'>📊</div>"
        "<div class='auth-title'>Excel Analyzer Pro 2026</div>"
        "<div class='auth-subtitle'>Analyze · Clean · Visualize · Report</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _login_form() -> None:
    """Render the login form and update session state on success."""
    with st.form("login_form"):
        st.markdown("#### Welcome back 👋")
        username = st.text_input("Username", placeholder="your username")
        password = st.text_input(
            "Password", type="password", placeholder="••••••••"
        )
        submitted = st.form_submit_button("Log in", type="primary")

    if submitted:
        result = auth.authenticate(username, password)
        if result.success:
            st.session_state["user"] = username.strip().lower()
            st.rerun()
        else:
            st.error(result.message)


def _register_form() -> None:
    """Render the registration form."""
    with st.form("register_form"):
        st.markdown("#### Create your account 🚀")
        username = st.text_input("Choose a username", placeholder="e.g. jdoe")
        password = st.text_input(
            "Choose a password", type="password", placeholder="min. 6 characters"
        )
        confirm = st.text_input(
            "Confirm password", type="password", placeholder="repeat password"
        )
        submitted = st.form_submit_button("Create account", type="primary")

    if submitted:
        if password != confirm:
            st.error("Passwords do not match.")
            return
        result = auth.register_user(username, password)
        (st.success if result.success else st.error)(result.message)


def render() -> bool:
    """Render the authentication gate.

    Returns:
        ``True`` if the user is authenticated, ``False`` otherwise.
    """
    if st.session_state.get("user"):
        return True

    # Theme switch in the top-right corner.
    _, toggle_col = st.columns([5, 1])
    with toggle_col:
        _theme_toggle()

    # Center the card with side spacers. On narrow screens Streamlit stacks
    # the columns, so the card naturally takes the full width (responsive).
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        _hero()
        login_tab, register_tab = st.tabs(["🔑  Login", "🆕  Register"])
        with login_tab:
            _login_form()
        with register_tab:
            _register_form()
        st.markdown(
            "<div class='auth-footer'>🔒 Your password is stored securely "
            "(salted PBKDF2 hash).</div>",
            unsafe_allow_html=True,
        )

    return False
