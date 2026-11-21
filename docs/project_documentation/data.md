# Data

## Files

| File | Lines | Columns | Content |
|---|---|---|---|
| `diabetes_part1.csv` | 50,000 | 9 | First half of the check-ups |
| `diabetes_part2.csv` | 50,000 | 9 | Second half of the check-ups |
| `gender_mapping.csv` | 3 | 2 | Mapping `gender_code` → `gender` |
| **final dataset** | 100,000 | 10 | The two parts stacked, with the `gender` column |

The files live in `data/` (not tracked by git). The 3 files are small enough (about 3 MB) to be loaded in memory.

## Data dictionary

### `diabetes_part*.csv`

| Column | Type | Values | Description |
|---|---|---|---|
| `gender_code` | text | `F`, `M`, `O` | Gender of the patient, coded (see the mapping) |
| `age` | float | years | Age of the patient |
| `hypertension` | int | `0`, `1` | `1` if the patient has hypertension |
| `heart_disease` | int | `0`, `1` | `1` if the patient has a heart disease |
| `smoking_history` | text | `never`, `former`, `current`, `not current`, `ever`, `No Info` | Smoking history |
| `bmi` | float | | Body Mass Index (kg/m²) |
| `HbA1c_level` | float | % | Average blood sugar over the last 2-3 months |
| `blood_glucose_level` | int | mg/dL | Blood glucose at the time of the check-up |
| `diabetes` | int | `0`, `1` | `1` if the patient is diabetic (the target variable) |

### `gender_mapping.csv`

| `gender_code` | `gender` |
|---|---|
| `F` | Female |
| `M` | Male |
| `O` | Other |

### Final dataset

The 9 columns above, plus `gender` (text), added by the merge.

## Transformation

```text
patients = concat(part1, part2, ignore_index=True)        # 100,000 lines
df_final = patients.merge(gender_mapping, on="gender_code", how="left")
```

- `ignore_index=True` renumbers the lines 0..99,999 instead of keeping two indexes starting at 0.
- A **left merge** keeps every patient, even if its code was not in the mapping. That is why the checks below are needed.

## Quality checks

| Check | Why | Where |
|---|---|---|
| Number of lines after the merge = number of lines of `patients` | A duplicated key in the mapping would multiply the lines | `assert` in versions 1-3, `ValueError` in the app |
| No missing `gender` | A code absent from the mapping would produce `NaN` | same |
| Required columns present (app only) | Uploaded files are user input | `read_csv` in the app |
| No part loaded twice (app only) | Loading a file twice would duplicate its patients | `load_data` in the app |

The app also displays these checks in its **Transformation** tab, with the number of missing values.

## Duplicates

3,854 lines are exact duplicates (all columns equal). **They are kept.** The dataset has no patient
identifier, so two different patients can have the same profile (same age, BMI, markers...). Removing the lines
would remove real patients and bias the prevalence. If an identifier existed, the decision should be reviewed.

## Using other data

The app accepts any number of parts as long as each one has the 9 columns above. For the scripts, the files
names and the 2-part structure are hard-coded in `load_data` / the load cell.
