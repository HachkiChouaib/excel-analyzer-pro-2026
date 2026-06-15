"""Unit tests for :mod:`utils.cleaner`."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from utils import cleaner


@pytest.fixture()
def messy_df() -> pd.DataFrame:
    """A DataFrame with duplicates and missing numeric values."""
    return pd.DataFrame(
        {
            "value": [1.0, 2.0, np.nan, 2.0],
            "label": ["a", "b", "c", "b"],
        }
    )


def test_remove_duplicates(messy_df: pd.DataFrame) -> None:
    cleaned = cleaner.remove_duplicates(messy_df)
    # Rows 2 and 4 are identical ("b", 2.0) -> one removed.
    assert len(cleaned) == 3


def test_handle_missing_drop(messy_df: pd.DataFrame) -> None:
    cleaned = cleaner.handle_missing(messy_df, "drop")
    assert cleaned["value"].isna().sum() == 0
    assert len(cleaned) == 3


def test_handle_missing_zero(messy_df: pd.DataFrame) -> None:
    cleaned = cleaner.handle_missing(messy_df, "zero")
    assert cleaned.loc[2, "value"] == 0


def test_handle_missing_mean(messy_df: pd.DataFrame) -> None:
    cleaned = cleaner.handle_missing(messy_df, "mean")
    # Mean of [1, 2, 2] = 1.666...
    assert cleaned["value"].isna().sum() == 0
    assert cleaned.loc[2, "value"] == pytest.approx((1 + 2 + 2) / 3)


def test_handle_missing_invalid_strategy(messy_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        cleaner.handle_missing(messy_df, "unknown")  # type: ignore[arg-type]


def test_rename_columns(messy_df: pd.DataFrame) -> None:
    renamed = cleaner.rename_columns(messy_df, {"value": "amount", "ghost": "x"})
    assert "amount" in renamed.columns
    assert "value" not in renamed.columns


def test_convert_column_to_number() -> None:
    df = pd.DataFrame({"v": ["1", "2", "bad"]})
    converted = cleaner.convert_column(df, "v", "number")
    assert converted["v"].isna().sum() == 1  # "bad" -> NaN
    assert converted["v"].iloc[0] == 1


def test_convert_column_missing_raises() -> None:
    df = pd.DataFrame({"v": [1, 2]})
    with pytest.raises(KeyError):
        cleaner.convert_column(df, "nope", "text")


def test_does_not_mutate_input(messy_df: pd.DataFrame) -> None:
    original = messy_df.copy()
    cleaner.handle_missing(messy_df, "zero")
    pd.testing.assert_frame_equal(messy_df, original)
