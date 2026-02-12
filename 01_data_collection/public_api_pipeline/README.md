# Public API Pipeline: KMA Surface Observation 

## Goal
This stage focuses on reliable raw data ingestion.
The primary objective is to collect original KMA surface observation text data and store it in its untouched form to preserve data integrity.

No cleaning, transformation, imputation, or aggregation is performed at this stage.
By strictly separating ingestion from processing, the pipeline prevents accidental distortion of source data and ensures reproducibility.

---
 
## Quality Design Principles

Raw data preservation: Original API responses are saved before any transformation.

Separation of concerns: Ingestion and cleaning stages are strictly divided.

Light parsing only (optional): CSV conversion is provided for convenience but does not modify values.

Reproducibility: Timestamp (tm) and station (stn) parameters are logged to maintain traceability.

## Setup (Auth Key)
This pipeline requires an API key.

### Option A) Environment variable (recommended)

---

**CMD**
```cmd
set KMA_AUTH_KEY=YOUR_KEY_HERE
python ingest.py --tm 202211300900 --stn 0 --save_csv

$env:KMA_AUTH_KEY="YOUR_KEY_HERE"
python ingest.py --tm 202211300900 --stn 0 --save_csv

python ingest.py --tm 202211300900 --stn 0 --auth_key "YOUR_KEY_HERE" --save_csv
