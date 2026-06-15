"""Cross-cutting helper utilities.

These functions are intentionally small and dependency-light. They handle
formatting, history persistence and column-type detection used across the app.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

# --- Project paths (resolved relative to the project root) ---------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
EXPORTS_DIR: Path = PROJECT_ROOT / "exports"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
HISTORY_FILE: Path = DATA_DIR / "history.json"


def ensure_directories() -> None:
    """Create the runtime directories if they do not already exist."""
    for directory in (DATA_DIR, EXPORTS_DIR, REPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def human_readable_size(num_bytes: float) -> str:
    """Convert a byte count into a human-readable string.

    Args:
        num_bytes: File size expressed in bytes.

    Returns:
        A formatted string such as ``"1.4 MB"``.
    """
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def format_number(value: Any) -> str:
    """Format a numeric value with thousands separators.

    Non-numeric values are returned as-is (cast to ``str``).

    Args:
        value: Any value; numbers are formatted, others are stringified.

    Returns:
        A display-friendly string.
    """
    if isinstance(value, (int,)) and not isinstance(value, bool):
        return f"{value:,}".replace(",", " ")
    if isinstance(value, float):
        return f"{value:,.2f}".replace(",", " ")
    return str(value)


def classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """Split DataFrame columns into numeric, datetime and text groups.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A mapping with keys ``"numeric"``, ``"datetime"`` and ``"text"``,
        each holding the matching column names.
    """
    numeric = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    # Anything not numeric/datetime is treated as text/categorical.
    text = [c for c in df.columns if c not in numeric and c not in datetime_cols]
    return {"numeric": numeric, "datetime": datetime_cols, "text": text}


def load_history() -> list[dict[str, Any]]:
    """Load the analysis history from disk.

    Returns:
        A list of history records, or an empty list if none exist yet.
    """
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        # Corrupted or unreadable history should never crash the app.
        return []


def append_history(filename: str, rows: int, columns: int) -> None:
    """Append a new entry to the persistent analysis history.

    Args:
        filename: Name of the analysed file.
        rows: Number of rows in the dataset.
        columns: Number of columns in the dataset.
    """
    ensure_directories()
    records = load_history()
    records.insert(
        0,
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename,
            "rows": rows,
            "columns": columns,
        },
    )
    # Keep only the 50 most recent analyses to bound file growth.
    records = records[:50]
    with HISTORY_FILE.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
