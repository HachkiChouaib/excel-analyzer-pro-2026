"""Unit tests for :mod:`utils.analyzer`."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from utils import analyzer


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """A small DataFrame with mixed types, missing values and a duplicate."""
    return pd.DataFrame(
        {
            "sales": [100, 200, 300, 200, np.nan],
            "profit": [10, 20, 30, 20, 5],
            "region": ["N", "S", "E", "S", "W"],
        }
    )


def test_general_info_counts(sample_df: pd.DataFrame) -> None:
    info = analyzer.general_info(sample_df)
    assert info["rows"] == 5
    assert info["columns"] == 3
    assert info["numeric_columns"] == 2
    assert info["text_columns"] == 1


def test_quality_report_detects_missing(sample_df: pd.DataFrame) -> None:
    quality = analyzer.quality_report(sample_df)
    assert quality["missing_total"] == 1
    assert quality["missing_percentage"] == pytest.approx(1 / 15 * 100, abs=0.01)
    assert "sales" in quality["missing_by_column"]


def test_numeric_statistics_values(sample_df: pd.DataFrame) -> None:
    stats = analyzer.numeric_statistics(sample_df)
    assert "mean" in stats.columns
    # Mean of profit = (10+20+30+20+5)/5 = 17.0
    assert stats.loc["profit", "mean"] == pytest.approx(17.0)


def test_detect_outliers_flags_extreme_value() -> None:
    df = pd.DataFrame({"x": [10, 11, 12, 13, 14, 1000]})
    outliers = analyzer.detect_outliers(df)
    assert outliers.get("x", 0) >= 1


def test_strong_correlations_finds_perfect_pair() -> None:
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 4, 6, 8]})
    pairs = analyzer.strong_correlations(df)
    assert pairs and pairs[0][2] == pytest.approx(1.0)


def test_analyze_dataset_reports_duplicates(sample_df: pd.DataFrame) -> None:
    insight = analyzer.analyze_dataset(sample_df)
    assert isinstance(insight.summary, str)
    # Missing value should surface as an issue.
    assert any("missing" in issue.lower() for issue in insight.issues)


def test_empty_numeric_returns_empty_stats() -> None:
    df = pd.DataFrame({"name": ["a", "b"]})
    assert analyzer.numeric_statistics(df).empty
    assert analyzer.correlation_matrix(df).empty
