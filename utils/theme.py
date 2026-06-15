"""Theme system: light / dark palettes and dynamic CSS generation.

The app exposes a single ``mode`` ("light" or "dark"). This module turns that
mode into a block of CSS custom properties plus the Streamlit-surface overrides
needed to recolour the whole UI. Kept UI-agnostic (pure strings, no Streamlit).
"""

from __future__ import annotations

from typing import Literal

ThemeMode = Literal["light", "dark"]

# --- Colour palettes ------------------------------------------------------
PALETTES: dict[str, dict[str, str]] = {
    "light": {
        "bg": "#f1f5f9",
        "bg_accent": "#e2e8f0",
        "card": "#ffffff",
        "text": "#0f172a",
        "muted": "#64748b",
        "border": "#e2e8f0",
        "input_bg": "#ffffff",
        "primary": "#4f46e5",
        "primary_2": "#2563eb",
        "shadow": "rgba(15, 23, 42, 0.10)",
    },
    "dark": {
        "bg": "#0b1220",
        "bg_accent": "#111c30",
        "card": "#1e293b",
        "text": "#e2e8f0",
        "muted": "#94a3b8",
        "border": "#334155",
        "input_bg": "#0f172a",
        "primary": "#818cf8",
        "primary_2": "#60a5fa",
        "shadow": "rgba(0, 0, 0, 0.45)",
    },
}


def build_css(mode: ThemeMode) -> str:
    """Build the dynamic theme CSS for the given mode.

    Args:
        mode: ``"light"`` or ``"dark"``.

    Returns:
        A CSS string (no surrounding ``<style>`` tags) defining the colour
        variables and overriding the main Streamlit surfaces.
    """
    p = PALETTES.get(mode, PALETTES["light"])
    return f"""
    :root {{
        --bg: {p['bg']};
        --bg-accent: {p['bg_accent']};
        --card: {p['card']};
        --text: {p['text']};
        --muted: {p['muted']};
        --border: {p['border']};
        --input-bg: {p['input_bg']};
        --primary: {p['primary']};
        --primary-2: {p['primary_2']};
        --shadow: {p['shadow']};
        --gradient: linear-gradient(135deg, {p['primary']} 0%, {p['primary_2']} 100%);
    }}

    /* --- App surfaces --- */
    .stApp,
    [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{
        background: var(--card) !important;
        border-right: 1px solid var(--border);
    }}

    /* --- Text colours --- */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
    [data-testid="stMarkdownContainer"] {{
        color: var(--text);
    }}
    .stApp .stCaption, .stApp small {{ color: var(--muted) !important; }}

    /* --- Inputs / selects --- */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    [data-baseweb="select"] > div {{
        background: var(--input-bg) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }}
    .stTextInput input::placeholder {{ color: var(--muted) !important; }}

    /* --- Metric / dataframe containers --- */
    [data-testid="stMetric"] {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.75rem 1rem;
    }}
    [data-testid="stMetricValue"] {{ color: var(--text); }}
    [data-testid="stMetricLabel"] {{ color: var(--muted); }}
    """
