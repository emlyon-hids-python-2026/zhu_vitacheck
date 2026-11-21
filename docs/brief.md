# Python Programming - Case Study: Diabetes Screening

- **Authors:** Constance de Taillac <constance.bartouilh@edu.em-lyon.com>
- **Version:** 2026-11

## 1. Context

You are a data analyst at **VitaCheck**, a network of preventive health centres operating in Europe.
Every year, thousands of patients come for a check-up: the centres measure their age, BMI, HbA1c level
and blood glucose level, record their medical history (hypertension, heart disease, smoking) and
test whether they have diabetes.

The Medical Director asks you for a reporting in order to:

- Know **how many patients** were screened and **how many are diabetic** (the *prevalence*)
- Understand **which profiles are most at risk**: gender, age, BMI, smoking history, hypertension
- Check that the **biological markers** (HbA1c, blood glucose) clearly separate diabetic and non-diabetic patients
- Share the results with the prevention teams so they can **target the next awareness campaign**

> [!NOTE]
> The **prevalence** of diabetes is the share of patients who are diabetic:
> `number of diabetic patients / number of patients`. Since `diabetes` is coded `0` / `1`,
> it is simply the **mean** of the `diabetes` column.

## 2. About the Data

The check-up data is split into 3 files:

| File | Content |
|---|---|
| `diabetes_part1.csv` | First half of the check-ups (50,000 lines) |
| `diabetes_part2.csv` | Second half of the check-ups (50,000 lines) |
| `gender_mapping.csv` | Mapping table between `gender_code` and `gender` |

Columns of `diabetes_part1.csv` and `diabetes_part2.csv`:

| Column | Description |
|---|---|
| `gender_code` | Gender of the patient, coded `F`, `M` or `O` (see `gender_mapping.csv`) |
| `age` | Age of the patient (in years) |
| `hypertension` | `1` if the patient has hypertension, `0` otherwise |
| `heart_disease` | `1` if the patient has a heart disease, `0` otherwise |
| `smoking_history` | `never`, `former`, `current`, `not current`, `ever` or `No Info` |
| `bmi` | Body Mass Index (weight in kg / height in m²) |
| `HbA1c_level` | Average blood sugar level over the last 2-3 months (in %) |
| `blood_glucose_level` | Blood glucose level at the time of the check-up (in mg/dL) |
| `diabetes` | `1` if the patient is diabetic, `0` otherwise |

Columns of `gender_mapping.csv`: `gender_code` (`F`, `M`, `O`) and `gender` (`Female`, `Male`, `Other`).

## 3. To download the data: 2 options

### With a Python script

1. Copy the script below
2. Create a `.py` script in the `scripts/` folder named `download_data.py`
3. Paste the script
4. Open a terminal
5. Run:

   **macOS / Linux:**

   ```bash
   cd scripts && uv run download_data.py && cd ..
   ```

   **Windows (PowerShell):**

   ```powershell
   cd scripts; uv run download_data.py; cd ..
   ```

### Manually

1. Download the 3 files from Brightspace
2. Paste them in the `data/` folder

### Reference: `download_data.py`

```python
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Download the `diabetes` dataset into ../data/.

Copy this file into your project folder and run:

    MacOS / Linux:
    cd scripts && uv run download_data.py && cd ..

    Windows:
    cd scripts ; uv run download_data.py ; cd ..

Files are saved to `../data/` (relative to this script) and overwritten if
they already exist. Only the Python standard library is used.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

OWNER = "emlyon-hids-python-2026"
REPO = "course_dataset"
BRANCH = "main"
FOLDER = "diabetes"

DEST = Path(__file__).resolve().parent.parent / "data"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FOLDER}?ref={BRANCH}"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "download_data.py"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def main():
    try:
        entries = json.loads(fetch(API_URL))
        files = [e for e in entries if e["type"] == "file"]
        DEST.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {len(files)} files to {DEST}")
        for entry in files:
            target = DEST / entry["name"]
            target.write_bytes(fetch(entry["download_url"]))
            print(f"  {entry['name']} ({target.stat().st_size:,} bytes)")
    except urllib.error.HTTPError as e:
        sys.exit(f"Download failed: HTTP {e.code} for {e.url}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")
    print("Done.")


if __name__ == "__main__":
    main()
```

## 4. Presentation of the Use Case: Technical pipeline

Until now, each centre sent its check-up results in separate files, and the team consolidated them
by hand in Excel: copy-paste of thousands of lines, replacing the gender codes one by one with
`VLOOKUP`... This workflow leads to many manual errors and takes a lot of time.

```text
diabetes_part1.csv ─┐
                    ├─ concat ──> patients ─┐
diabetes_part2.csv ─┘                       ├─ merge (on gender_code) ──> final dataset ──> Excel
                      gender_mapping.csv ───┘
```

## 5. Objective 1: Automate the consolidation process

1. Assemble the 3 files together into 1 unique table:

   - Load the data (`diabetes_part1`, `diabetes_part2` and `gender_mapping`)
   - Assemble `diabetes_part1` and `diabetes_part2` together into `patients` (**concatenation**)
   - Assemble the `patients` table with the mapping table to get the `gender` column (**merge**)

2. Export the resulting table in an Excel file that could be used by any other team member.

> [!TIP]
> Look at `pd.concat`, `pd.merge` (or `DataFrame.merge`).
> After the merge, check that **no line was lost** and that the `gender` column has **no missing value**.

## 6. Objective 2: Answer some questions

### Technical questions from the Data Team

1. What is the number of lines and columns in our original datasets and in our final dataset?
2. What are the column names in the final dataset?
3. What are the top 5 lines of our dataset?
4. What are the last 5 lines of our dataset?
5. Make a general statistical description of all the dataset.
6. How many lines are exact duplicates? Should we keep them? (Explain your choice.)

### Business questions from the Medical Team

1. How many patients were screened?
2. How many patients are diabetic, and what is the prevalence of diabetes?
3. What is the prevalence of diabetes for women and for men?
4. What is the average age of diabetic patients compared to non-diabetic patients?
5. What is the prevalence of diabetes for patients with a BMI of 30 or more (obese) compared to patients with a BMI below 30?
6. What is the average `HbA1c_level` and `blood_glucose_level` of diabetic patients compared to non-diabetic patients?
7. How many times higher is the prevalence of diabetes for patients with hypertension than for patients without?
8. Which `smoking_history` category has the highest prevalence of diabetes? Is it the one you expected?

## 7. Objective 3 (optional): Make some graph analysis

- Make a graph of the number of patients per gender
- Make a graph of the prevalence of diabetes per gender
- Make a graph comparing the distribution of `age` for diabetic and non-diabetic patients
- Make a graph comparing the distribution of `blood_glucose_level` for diabetic and non-diabetic patients

## 8. Objective 4: Export your analysis

The prevention teams would like you to export your analysis tables and your graphs in Excel so that
they can easily include your results in their next presentation (PowerPoint) for the board.

- Export the final combined dataset into an Excel file.
- **Technical team questions:** export questions 1 and 5 into distinct Excel tables, or into different sheets of the same Excel file.
- **Medical team questions:** export the questions and their answers in the same Excel file.

> [!NOTE]
> Writing Excel files with pandas needs the `openpyxl` package: `uv add openpyxl`.

## 9. To help you export the data: create a dictionary, then a dataframe

```python
# %% Create a dictionary to store the analysis results
dict_analysis = {
    "How many lines are in diabetes_part1.csv": nb_lines_part1,
    "How many lines are in diabetes_part2.csv": nb_lines_part2,
    "How many lines are in gender_mapping.csv": nb_lines_mapping,
    "How many patients were screened": nb_patients,
    "How many patients are diabetic": nb_diabetic,
    "What is the prevalence of diabetes": prevalence,
    "What is the prevalence of diabetes for women": prevalence_women,
    "What is the prevalence of diabetes for men": prevalence_men,
}

# %% Convert the dictionary to a DataFrame for better visualization
df_analysis = pd.DataFrame(list(dict_analysis.items()), columns=["Question", "Answer"])

# %% Export several tables into several sheets of the same Excel file
with pd.ExcelWriter("data/analysis.xlsx") as writer:
    df_analysis.to_excel(writer, sheet_name="business_questions", index=False)
    df_describe.to_excel(writer, sheet_name="statistics")
```
