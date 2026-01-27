# Data Cleaning Policy (KMA sfctm2)

## 1. Purpose
This stage defines a minimal and transparent cleaning policy for KMA surface observation data.
The goal is not to "make the data pretty" but to ensure that downstream analysis is not distorted
by placeholder values and inconsistent types.

This project treats cleaning as a set of explicit decisions that should be auditable.

---

## 2. What we have in raw data
Raw files are ingested as text and saved without modification.

A single observation (row) represents:
- one timestamp (TM, KST)
- one station (STN)
- multiple observed variables (wind, temperature, humidity, precipitation, etc.)

Unit of observation:
(TM, STN)

---

## 3. Expected data issues
### 3.1 Placeholder missing codes
KMA text outputs often use numeric placeholders such as:
- -9, -9.0, -9.00
- -99, -99.0
These should be interpreted as missing / not observed / not applicable depending on the variable.

Policy:
- Convert placeholder codes to proper missing values (NaN) in the analysis-ready dataset.

### 3.2 Type consistency
Because raw data are read as strings or mixed types:
- numeric columns may include non-numeric symbols or placeholders
- some columns are categorical codes (e.g., weather codes) even if they look numeric

Policy:
- Keep raw as-is.
- In cleaned layer, explicitly cast:
  - TM -> string (or datetime later)
  - STN -> integer
  - continuous variables -> float
  - code/categorical variables -> string or category

### 3.3 Token/format mismatch
Some rows may not match the expected number of tokens due to formatting differences.

Policy:
- Do not "fix" them during ingestion.
- In parsing/cleaning, log how many rows were skipped and why.

---

## 4. What we do NOT do in this stage
To keep assumptions minimal, we do not:
- impute missing values
- remove outliers
- aggregate over time or stations
- enforce domain constraints (e.g., humidity range)
These will be handled later when analysis goals are specified.

---

## 5. Outputs of cleaning stage
This stage will produce:
- a cleaned table with consistent types
- placeholder missing codes converted to NaN
- a simple data-quality report (counts of missing per column, parse skip counts)

Directory suggestion:
- data_clean/ : cleaned csv/parquet
- reports/    : summary logs (missing counts, parse stats)

---

## 6. Rationale
KMA data are observational and sensor-based.
Missingness and extreme values may reflect real-world processes, not mere errors.
Therefore, we treat cleaning as an explicit policy rather than a one-off preprocessing step.
