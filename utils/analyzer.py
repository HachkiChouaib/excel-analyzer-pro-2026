"""Data analysis engine.

Computes descriptive statistics, data-quality metrics and a rule-based
"AI" assessment (summary, detected issues and recommendations). Pure pandas /
numpy — no UI dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from utils.helpers import classify_columns

# Threshold above which a column's missing ratio is flagged as problematic.
MISSING_WARN_RATIO: float = 0.10
# Absolute Pearson correlation above which a pair is reported as "strong".
STRONG_CORR_THRESHOLD: float = 0.70


# ---------------------------------------------------------------------------
# General information & quality
# ---------------------------------------------------------------------------
def general_info(df: pd.DataFrame) -> dict[str, Any]:
    """Compute high-level structural information about the dataset.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A dictionary with row/column counts and per-type column counts.
    """
    groups = classify_columns(df)
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numeric_columns": len(groups["numeric"]),
        "text_columns": len(groups["text"]),
        "datetime_columns": len(groups["datetime"]),
        "memory_usage": int(df.memory_usage(deep=True).sum()),
    }


def quality_report(df: pd.DataFrame) -> dict[str, Any]:
    """Assess data quality: missing values, duplicates and empty columns.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A dictionary describing quality metrics, including a per-column
        breakdown of missing values.
    """
    total_cells = int(df.size) or 1  # avoid division by zero on empty frames
    missing_per_column = df.isna().sum()
    total_missing = int(missing_per_column.sum())

    return {
        "missing_total": total_missing,
        "missing_percentage": round(total_missing / total_cells * 100, 2),
        "duplicates": int(df.duplicated().sum()),
        "empty_columns": [c for c in df.columns if df[c].isna().all()],
        "missing_by_column": {
            col: int(count)
            for col, count in missing_per_column.items()
            if count > 0
        },
    }


def numeric_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics for numeric columns.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A DataFrame indexed by column name with ``mean``, ``median``,
        ``min``, ``max`` and ``std`` columns. Empty if no numeric columns.
    """
    numeric_cols = classify_columns(df)["numeric"]
    if not numeric_cols:
        return pd.DataFrame()

    numeric_df = df[numeric_cols]
    stats = pd.DataFrame(
        {
            "mean": numeric_df.mean(numeric_only=True),
            "median": numeric_df.median(numeric_only=True),
            "min": numeric_df.min(numeric_only=True),
            "max": numeric_df.max(numeric_only=True),
            "std": numeric_df.std(numeric_only=True),
        }
    )
    return stats.round(2)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return the Pearson correlation matrix of numeric columns.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A square correlation DataFrame, or an empty one if fewer than two
        numeric columns are present.
    """
    numeric_cols = classify_columns(df)["numeric"]
    if len(numeric_cols) < 2:
        return pd.DataFrame()
    return df[numeric_cols].corr(numeric_only=True).round(2)


# ---------------------------------------------------------------------------
# Outlier detection (IQR method)
# ---------------------------------------------------------------------------
def detect_outliers(df: pd.DataFrame) -> dict[str, int]:
    """Count outliers per numeric column using the 1.5*IQR rule.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A mapping ``{column: outlier_count}`` for columns that have at
        least one outlier.
    """
    outliers: dict[str, int] = {}
    for col in classify_columns(df)["numeric"]:
        series = df[col].dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue  # constant column → no meaningful spread
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        count = int(((series < lower) | (series > upper)).sum())
        if count > 0:
            outliers[col] = count
    return outliers


def strong_correlations(df: pd.DataFrame) -> list[tuple[str, str, float]]:
    """Find pairs of numeric columns with a strong linear correlation.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A list of ``(column_a, column_b, correlation)`` tuples whose absolute
        correlation exceeds :data:`STRONG_CORR_THRESHOLD`.
    """
    corr = correlation_matrix(df)
    if corr.empty:
        return []

    pairs: list[tuple[str, str, float]] = []
    columns = corr.columns.tolist()
    # Iterate over the upper triangle only to avoid duplicate/self pairs.
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            value = corr.iloc[i, j]
            if pd.notna(value) and abs(value) >= STRONG_CORR_THRESHOLD:
                pairs.append((columns[i], columns[j], round(float(value), 2)))
    return sorted(pairs, key=lambda p: abs(p[2]), reverse=True)


# ---------------------------------------------------------------------------
# Rule-based "AI" assessment  (Module 6)
# ---------------------------------------------------------------------------
@dataclass
class AIInsight:
    """Structured result of the automated analytical assessment.

    Attributes:
        summary: One-line dataset overview.
        issues: Human-readable problems detected in the data.
        recommendations: Suggested next actions.
    """

    summary: str
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def analyze_dataset(df: pd.DataFrame) -> AIInsight:
    """Generate an automated analytical assessment of the dataset.

    The logic is deterministic and rule-based (no external API): it inspects
    missing values, duplicates, outliers and correlations to produce a
    natural-language style report.

    Args:
        df: The DataFrame to analyse.

    Returns:
        An :class:`AIInsight` with a summary, detected issues and
        recommendations.
    """
    info = general_info(df)
    quality = quality_report(df)

    summary = (
        f"The dataset contains {info['rows']:,} rows and "
        f"{info['columns']} columns "
        f"({info['numeric_columns']} numeric, {info['text_columns']} text, "
        f"{info['datetime_columns']} datetime)."
    )

    issues: list[str] = []
    recommendations: list[str] = []

    # --- Missing values ---------------------------------------------------
    missing_pct = quality["missing_percentage"]
    if missing_pct > 0:
        issues.append(f"The dataset contains {missing_pct}% of missing values.")
        if missing_pct >= MISSING_WARN_RATIO * 100:
            recommendations.append(
                "Consider imputing or dropping missing values before analysis."
            )

    # --- Empty columns ----------------------------------------------------
    if quality["empty_columns"]:
        cols = ", ".join(quality["empty_columns"])
        issues.append(f"The following columns are entirely empty: {cols}.")
        recommendations.append("Drop empty columns to reduce noise.")

    # --- Duplicates -------------------------------------------------------
    if quality["duplicates"] > 0:
        issues.append(f"{quality['duplicates']} duplicate rows were found.")
        recommendations.append("Remove duplicate rows to avoid biased statistics.")

    # --- Outliers ---------------------------------------------------------
    outliers = detect_outliers(df)
    for column, count in outliers.items():
        issues.append(
            f"The column '{column}' has {count} potential outlier value(s)."
        )
    if outliers:
        recommendations.append(
            "Inspect flagged outliers; they may be errors or genuine extremes."
        )

    # --- Correlations -----------------------------------------------------
    for col_a, col_b, value in strong_correlations(df):
        direction = "positive" if value > 0 else "negative"
        issues.append(
            f"A strong {direction} correlation ({value}) is observed "
            f"between '{col_a}' and '{col_b}'."
        )

    if not issues:
        issues.append("No major data-quality issues were detected. ")
        recommendations.append("The dataset looks clean and ready for analysis.")

    return AIInsight(summary=summary, issues=issues, recommendations=recommendations)
