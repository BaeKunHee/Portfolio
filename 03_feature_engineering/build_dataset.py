import os
import argparse
import pandas as pd


CORE_VARS = [
    "TM", "STN",
    "TA",   # Air temperature
    "WS",   # Wind speed
    "HM",   # Relative humidity
    "PA",   # Pressure (station)
    "PS",   # Pressure (sea level)
]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="Build base hourly dataset from cleaned KMA data"
    )
    parser.add_argument(
        "--input_clean",
        required=True,
        help="Path to cleaned CSV from 02_data_cleaning"
    )
    parser.add_argument(
        "--output_dir",
        default="datasets",
        help="Directory to save feature datasets"
    )
    args = parser.parse_args()

    ensure_dir(args.output_dir)

    # 1) Load cleaned data
    df = pd.read_csv(args.input_clean, parse_dates=["TM"])

    # 2) Select core variables
    missing_cols = [c for c in CORE_VARS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    base = df[CORE_VARS].copy()

    # 3) Basic sanity checks (no filtering)
    base = base.sort_values(["TM", "STN"]).reset_index(drop=True)

    # 4) Save dataset
    out_path = os.path.join(args.output_dir, "hourly_base.parquet")
    base.to_parquet(out_path, index=False)

    print(f"[OK] Base hourly dataset saved: {out_path}")
    print(f"[INFO] Rows: {len(base)}, Columns: {len(base.columns)}")


if __name__ == "__main__":
    main()
