import os
import json
import glob
import argparse
from datetime import datetime

import pandas as pd


# --- Project policy: placeholder missing codes ---
# KMA text outputs often use numeric placeholders like -9 / -99 (and their float forms).
DEFAULT_MISSING_VALUES = [-9, -9.0, -9.00, -99, -99.0, -99.00]


def ensure_dirs(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)


def load_latest_csv(input_dir: str) -> str:
    """Pick the most recently modified csv in input_dir."""
    pattern = os.path.join(input_dir, "*.csv")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No CSV files found in: {input_dir}")
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return files[0]


def coerce_numeric_columns(df: pd.DataFrame, exclude: set[str]) -> pd.DataFrame:
    """
    Convert all columns except excluded to numeric if possible.
    Non-convertible values become NaN (errors='coerce').
    """
    out = df.copy()
    for c in out.columns:
        if c in exclude:
            continue
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def build_quality_report(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> dict:
    """Create a minimal quality report useful for downstream decisions."""
    report = {}

    report["rows_raw"] = int(len(raw_df))
    report["rows_clean"] = int(len(clean_df))
    report["cols"] = list(clean_df.columns)

    # Time coverage
    tm = clean_df.get("TM")
    if tm is not None and pd.api.types.is_datetime64_any_dtype(tm):
        report["tm_min"] = None if tm.isna().all() else tm.min().isoformat()
        report["tm_max"] = None if tm.isna().all() else tm.max().isoformat()
    else:
        report["tm_min"] = None
        report["tm_max"] = None

    # Station coverage
    if "STN" in clean_df.columns:
        stn_valid = clean_df["STN"].dropna()
        report["n_stations"] = int(stn_valid.nunique()) if len(stn_valid) else 0
    else:
        report["n_stations"] = 0

    # Missingness
    miss_cnt = clean_df.isna().sum().sort_values(ascending=False)
    miss_rate = (clean_df.isna().mean() * 100).round(3).sort_values(ascending=False)

    report["missing_count"] = {k: int(v) for k, v in miss_cnt.items()}
    report["missing_rate_percent"] = {k: float(v) for k, v in miss_rate.items()}

    # Basic numeric sanity snapshot (no outlier removal, just record)
    numeric_cols = [c for c in clean_df.columns if pd.api.types.is_numeric_dtype(clean_df[c])]
    snapshot = {}
    for c in numeric_cols:
        s = clean_df[c]
        if s.notna().any():
            snapshot[c] = {
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": float(s.mean()),
            }
        else:
            snapshot[c] = {"min": None, "max": None, "mean": None}
    report["numeric_snapshot"] = snapshot

    return report


def main():
    parser = argparse.ArgumentParser(description="Clean KMA sfctm2 parsed CSV (placeholder->NaN, types, report).")
    parser.add_argument("--input_dir", required=True, help="Directory that contains parsed CSVs from ingest step.")
    parser.add_argument("--input_file", default=None, help="Optional: specific CSV file to clean.")
    parser.add_argument("--output_dir", default="data_clean", help="Output directory for cleaned data.")
    parser.add_argument("--report_dir", default="reports", help="Output directory for reports.")
    parser.add_argument("--missing_values", default=None,
                        help="Comma-separated placeholder values to treat as missing. "
                             "Default: -9,-99 (and float forms)")
    args = parser.parse_args()

    ensure_dirs(args.output_dir, args.report_dir)

    # 1) Locate input
    if args.input_file:
        in_path = args.input_file
        if not os.path.exists(in_path):
            raise FileNotFoundError(f"Input file not found: {in_path}")
    else:
        in_path = load_latest_csv(args.input_dir)

    # 2) Read
    raw_df = pd.read_csv(in_path, dtype=str)  # keep raw as string first (safer)
    df = raw_df.copy()

    # 3) Missing placeholders -> NaN
    if args.missing_values:
        mv = []
        for x in args.missing_values.split(","):
            x = x.strip()
            if x == "":
                continue
            # accept numeric tokens like -9, -9.0
            try:
                mv.append(float(x))
            except ValueError:
                pass
        missing_values = mv
    else:
        missing_values = DEFAULT_MISSING_VALUES

    # We'll replace placeholders after numeric coercion.
    # (Because raw is string; we first convert columns to numeric where appropriate.)

    # 4) Type casting policy (minimal)
    # TM: parse datetime from YYYYMMDDHHMI (KST)
    if "TM" in df.columns:
        # Keep raw TM string, create parsed datetime column as TM_DT then rename to TM
        tm_str = df["TM"].astype(str)
        tm_dt = pd.to_datetime(tm_str, format="%Y%m%d%H%M", errors="coerce")
        df["TM"] = tm_dt

    # STN: station id
    if "STN" in df.columns:
        df["STN"] = pd.to_numeric(df["STN"], errors="coerce").astype("Int64")

    # 5) Coerce other columns to numeric where possible
    exclude = {"TM", "STN", "CT", "WW"}  # keep known string-like columns as-is (policy can evolve)
    df = coerce_numeric_columns(df, exclude=exclude)

    # 6) Replace placeholder numeric codes with NaN (only affects numeric columns)
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].replace(missing_values, pd.NA)

    # 7) Save cleaned data
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(os.path.basename(in_path))[0]
    out_csv = os.path.join(args.output_dir, f"{base}__clean__{ts}.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[OK] Cleaned saved: {out_csv}")

    # 8) Save quality report
    report = build_quality_report(raw_df=raw_df, clean_df=df)
    report["input_file"] = os.path.abspath(in_path)
    report["output_file"] = os.path.abspath(out_csv)
    report["generated_at"] = datetime.now().isoformat()
    report["missing_values_policy"] = missing_values
    report["excluded_non_numeric_columns_policy"] = sorted(list(exclude))

    out_report = os.path.join(args.report_dir, f"{base}__report__{ts}.json")
    with open(out_report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[OK] Report saved: {out_report}")


if __name__ == "__main__":
    main()

