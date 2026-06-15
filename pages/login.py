"""Login / Register screen (Portfolio bonus: authentication)."""

from __future__ import annotations

import streamlit as st

from utils import auth


def _login_form() -> None:
    """Render the login form and update session state on success."""
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
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
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password (min. 6 chars)", type="password")
        confirm = st.text_input("Confirm password", type="password")
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

    st.markdown("<div class='app-brand'>📊 Excel Analyzer Pro 2026</div>",
                unsafe_allow_html=True)
    st.caption("Sign in to access your personal dashboard, files and reports.")

    login_tab, register_tab = st.tabs(["🔑 Login", "🆕 Register"])
    with login_tab:
        _login_form()
    with register_tab:
        _register_form()

    return False
