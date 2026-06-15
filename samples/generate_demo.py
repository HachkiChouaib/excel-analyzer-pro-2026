"""Generate a demo dataset for Excel Analyzer Pro 2026.

The dataset deliberately contains missing values, duplicate rows, outliers and
correlated columns so that every analysis feature has something to surface.

Run:
    python samples/generate_demo.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT_FILE = Path(__file__).resolve().parent / "demo_sales.xlsx"
RNG = np.random.default_rng(42)
N_ROWS = 200


def build_demo_dataframe() -> pd.DataFrame:
    """Build the synthetic sales DataFrame.

    Returns:
        A DataFrame with mixed types and intentional data-quality issues.
    """
    regions = RNG.choice(["North", "South", "East", "West"], size=N_ROWS)
    categories = RNG.choice(["Hardware", "Software", "Services"], size=N_ROWS)

    sales = RNG.normal(5_000, 1_500, size=N_ROWS).round(2)
    # Profit is strongly correlated with sales (plus some noise).
    profit = (sales * 0.22 + RNG.normal(0, 120, size=N_ROWS)).round(2)
    units = RNG.integers(1, 50, size=N_ROWS)

    df = pd.DataFrame(
        {
            "order_date": pd.date_range("2025-01-01", periods=N_ROWS, freq="D"),
            "region": regions,
            "category": categories,
            "sales": sales,
            "profit": profit,
            "units": units,
        }
    )

    # --- Inject data-quality issues ---
    # 1) Missing values in 'sales'.
    missing_idx = RNG.choice(N_ROWS, size=12, replace=False)
    df.loc[missing_idx, "sales"] = np.nan

    # 2) A few extreme outliers in 'profit'.
    df.loc[RNG.choice(N_ROWS, size=3, replace=False), "profit"] = 50_000

    # 3) Duplicate rows.
    df = pd.concat([df, df.iloc[:5]], ignore_index=True)

    return df


def main() -> None:
    """Generate and save the demo Excel file."""
    df = build_demo_dataframe()
    df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
    print(f"Demo dataset written to: {OUTPUT_FILE} ({len(df)} rows)")


if __name__ == "__main__":
    main()
