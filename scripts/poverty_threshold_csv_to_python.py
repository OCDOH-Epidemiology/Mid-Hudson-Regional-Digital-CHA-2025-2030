import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _coerce_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "NaN": np.nan})
        .str.replace(r"[$,]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _format_value(value) -> str:
    if pd.isna(value):
        return "np.nan"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return repr(value)


def csv_to_python(csv_path: Path) -> str:
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"No data found in {csv_path}")

    first_col = df.columns[0]
    size_values = df[first_col].fillna("").astype(str).tolist()

    numeric_cols = [col for col in df.columns if col != first_col]
    for col in numeric_cols:
        df[col] = _coerce_numeric(df[col])

    lines = ["data = {", '    " ": [']
    for value in size_values:
        lines.append(f"        {repr(value)},")
    lines.append("    ],")

    for col in numeric_cols:
        lines.append(f'    ("Related children under 18 years", "{col}"): [')
        for value in df[col].tolist():
            lines.append(f"        {_format_value(value)},")
        lines.append("    ],")

    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    parser = argparse.ArgumentParser(
        description="Convert the poverty threshold CSV to a Python dict snippet."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=project_root / "data" / "poverty_threshold_2024.csv",
        help="Path to the CSV file exported from Excel.",
    )
    args = parser.parse_args()

    output = csv_to_python(Path(args.csv_path))
    print(output)


if __name__ == "__main__":
    main()
