# Public API Pipeline: KMA Surface Observation (sfctm2)

## Goal
Collect raw KMA surface observation text data and store it as raw files.
Optionally, parse the data rows into a CSV (light parsing).

This stage does **not** perform cleaning, imputation, or aggregation.

---

## Setup (Auth Key)
This pipeline requires an API key.

### Option A) Environment variable (recommended)
**CMD**
```cmd
set KMA_AUTH_KEY=YOUR_KEY_HERE
python ingest.py --tm 202211300900 --stn 0 --save_csv

$env:KMA_AUTH_KEY="YOUR_KEY_HERE"
python ingest.py --tm 202211300900 --stn 0 --save_csv

python ingest.py --tm 202211300900 --stn 0 --auth_key "YOUR_KEY_HERE" --save_csv
