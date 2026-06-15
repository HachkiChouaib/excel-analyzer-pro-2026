"""Data cleaning operations.

Every function returns a *new* DataFrame (never mutates its input) so that
operations remain side-effect free and easy to test or undo.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd

# Allowed strategies for handling missing values.
MissingStrategy = Literal["drop", "mean", "median", "zero"]
# Allowed target types for column conversion.
TargetType = Literal["text", "number", "date"]


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with duplicate rows removed.

    Args:
        df: The input DataFrame.

    Returns:
        A new DataFrame without duplicate rows (index reset).
    """
    return df.drop_duplicates().reset_index(drop=True)


def handle_missing(df: pd.DataFrame, strategy: MissingStrategy) -> pd.DataFrame:
    """Handle missing values according to the chosen strategy.

    Args:
        df: The input DataFrame.
        strategy: One of ``"drop"``, ``"mean"``, ``"median"`` or ``"zero"``.
            ``"mean"`` and ``"median"`` only affect numeric columns.

    Returns:
        A new DataFrame with missing values handled.

    Raises:
        ValueError: If an unknown strategy is provided.
    """
    result = df.copy()

    if strategy == "drop":
        return result.dropna().reset_index(drop=True)

    if strategy == "zero":
        return result.fillna(0)

    if strategy in ("mean", "median"):
        numeric_cols = result.select_dtypes(include="number").columns
        for col in numeric_cols:
            fill_value = (
                result[col].mean() if strategy == "mean" else result[col].median()
            )
            result[col] = result[col].fillna(fill_value)
        return result

    raise ValueError(f"Unknown missing-value strategy: {strategy!r}")


def rename_columns(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Rename columns using the provided mapping.

    Args:
        df: The input DataFrame.
        mapping: A ``{old_name: new_name}`` mapping. Unknown keys are ignored.

    Returns:
        A new DataFrame with renamed columns.
    """
    # Only keep mappings whose source column actually exists.
    valid = {old: new for old, new in mapping.items() if old in df.columns}
    return df.rename(columns=valid)


def convert_column(df: pd.DataFrame, column: str, target: TargetType) -> pd.DataFrame:
    """Convert a single column to a target data type.

    Invalid values become ``NaN`` (numbers/dates) rather than raising, which is
    the safer behaviour for messy real-world data.

    Args:
        df: The input DataFrame.
        column: Name of the column to convert.
        target: One of ``"text"``, ``"number"`` or ``"date"``.

    Returns:
        A new DataFrame with the column converted.

    Raises:
        KeyError: If the column does not exist.
        ValueError: If an unknown target type is provided.
    """
    if column not in df.columns:
        raise KeyError(f"Column {column!r} does not exist.")

    result = df.copy()
    if target == "text":
        result[column] = result[column].astype("string")
    elif target == "number":
        result[column] = pd.to_numeric(result[column], errors="coerce")
    elif target == "date":
        result[column] = pd.to_datetime(result[column], errors="coerce")
    else:
        raise ValueError(f"Unknown target type: {target!r}")

    return result


def drop_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Drop the given columns if they exist.

    Args:
        df: The input DataFrame.
        columns: Column names to drop (missing ones are ignored).

    Returns:
        A new DataFrame without the specified columns.
    """
    to_drop = [c for c in columns if c in df.columns]
    return df.drop(columns=to_drop)
