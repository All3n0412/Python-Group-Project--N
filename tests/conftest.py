"""Shared helpers: build small fake form files for the tests."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SAMPLE = ROOT / "data" / "sample" / "sample_responses.xlsx"


def make_responses(players, **extra_columns):
    """players: list of (gender, level, attitude). Returns a form-like DataFrame."""
    rows = []
    for i, (gender, level, attitude) in enumerate(players, start=1):
        rows.append({
            "Timestamp": pd.Timestamp("2026-11-01") + pd.Timedelta(minutes=i),
            "Name": f"P{i:02d}",
            "Student ID": f"B13{i:06d}",
            "Gender": gender,
            "Self-rated level (1-5)": level,
            "Attitude": attitude,
        })
    df = pd.DataFrame(rows)
    for col, values in extra_columns.items():
        df[col] = values
    return df


@pytest.fixture
def write_xlsx(tmp_path):
    """Save a DataFrame to a temporary .xlsx and return its path."""
    def _write(df, name="responses.xlsx"):
        path = tmp_path / name
        df.to_excel(path, index=False)
        return path
    return _write
