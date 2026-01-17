import os
import re
import argparse
from datetime import datetime

import requests
import pandas as pd

from utils.env import get_kma_auth_key

BASE_URL = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php"


def is_data_row(line: str) -> bool:
    """Data rows start with 12 digits: e.g., 202211300900 ..."""
    return bool(re.match(r"^\d{12}\s+", line.strip()))


def parse_rows_to_df(lines: list[str]) -> pd.DataFrame:
    """
    Light parser:
    - whitespace split
    - skip rows whose token length does not match expected columns
    """
    cols = [
        "TM", "STN", "WD", "WS",
        "GST_WD", "GST_WS", "GST_TM",
        "PA", "PS", "PT", "PR",
        "TA", "TD", "HM", "PV",
        "RN", "RN_DAY", "RN_JUN", "RN_INT",
        "SD_HR3", "SD_DAY", "SD_TOT",
        "WC", "WP", "WW",
        "CA_TOT", "CA_MID", "CH_MIN",
        "CT", "CT_TOP", "CT_MID", "CT_LOW",
        "VS", "SS", "SI", "ST_GD",
        "TS", "TE_005", "TE_01", "TE_02", "TE_03",
        "ST_SEA", "WH", "BF", "IR", "IX"
    ]

    rows = []
    for ln in lines:
        parts = ln.strip().split()
        if len(parts) != len(cols):
            continue
        rows.append(parts)

    df = pd.DataFrame(rows, columns=cols)

    # Keep most columns as strings at ingest stage (raw-ish).
    df["TM"] = df["TM"].astype(str)
    df["STN"] = pd.to_numeric(df["STN"], errors="coerce").astype("Int64")

    return df


def main():
    parser = argparse.ArgumentParser(description="Ingest KMA sfctm2 (raw text + optional parsed csv).")
    parser.add_argument("--tm", required=True, help="Observation time, e.g., 202211300900")
    parser.add_argument("--stn", default="0", help="Station ID (0 for all).")
    parser.add_argument("--help_flag", default="1", help="help=1 to include header description.")
    parser.add_argument("--auth_key", default=None, help="If not provided, reads env KMA_AUTH_KEY.")
    parser.add_argument("--out_dir", default="data_raw", help="Output directory for raw files.")
    parser.add_argument("--save_csv", action="store_true", help="Also save parsed CSV if possible.")
    args = parser.parse_args()

    auth_key = args.auth_key or get_kma_auth_key()

    os.makedirs(args.out_dir, exist_ok=True)

    params = {"tm": args.tm, "stn": args.stn, "help": args.help_flag, "authKey": auth_key}

    resp = requests.get(BASE_URL, params=params, timeout=30)

    # Helpful debug info (safe: does not print authKey)
    if resp.status_code != 200:
        print("Status:", resp.status_code)
        print("Response preview:", resp.text[:300])

    resp.raise_for_status()
    text = resp.text

    # 1) Save raw text (ALWAYS)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = os.path.join(args.out_dir, f"kma_sfctm2_raw_tm{args.tm}_stn{args.stn}_{ts}.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[OK] Raw saved: {raw_path}")

    # 2) Parse only data rows (OPTIONAL)
    if args.save_csv:
        data_lines = [ln for ln in text.splitlines() if is_data_row(ln)]
        df = parse_rows_to_df(data_lines)

        csv_path = os.path.join(args.out_dir, f"kma_sfctm2_parsed_tm{args.tm}_stn{args.stn}_{ts}.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")

        print(f"[OK] Parsed CSV saved: {csv_path}")
        print(f"[INFO] Parsed rows: {len(df)}")
        if len(df) == 0:
            print("[WARN] No rows parsed. Token mismatch lines were skipped.")


if __name__ == "__main__":
    main()

