# Getting started

## 1. Prerequisites

| Tool | Why | How |
|---|---|---|
| `uv` | Installs Python and the dependencies | See the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/) or `.vscode/ReadMe.MD` |
| Python 3.14 | Version pinned in `.python-version` | Installed automatically by `uv` |
| VSCode (recommended) | Notebook and `# %%` cells | The recommended extensions are listed in `.vscode/extensions.json` |

## 2. Install

```bash
git clone <repository-url>
cd do_course06
uv sync
```

`uv sync` creates the `.venv/` virtual environment and installs the versions locked in `uv.lock`.

## 3. Get the data

The `data/` folder is ignored by git. Put the 3 CSV files in it:

```text
data/
├── diabetes_part1.csv
├── diabetes_part2.csv
└── gender_mapping.csv
```

Two options (detailed in [brief.md](../brief.md#3-to-download-the-data-2-options)):

- download the files from Brightspace and paste them in `data/`
- or run the download script from the brief: `cd scripts && uv run download_data.py && cd ..`

> The Streamlit app does not read `data/`: you load the files in its sidebar. The versions 1, 2 and 3 read `data/`.

## 4. Run

| Version | Command |
|---|---|
| 1. Notebook | Open `notebooks/01_diabetes_notebook.ipynb` in VSCode, select the `.venv` kernel, *Run All* |
| 2. Script with cells | `make run_v2` (or *Run Cell* above each `# %%` in VSCode) |
| 3. Script with functions | `make run_v3` |
| 4. Streamlit app | `make run_app` |

Without `make`: `uv run scripts/02_diabetes_cells.py`, `uv run scripts/03_diabetes_functions.py`,
`uv run streamlit run app/app.py`.

Run everything from the **project root**.

## 5. Results

Versions 1, 2 and 3 write in `data/output_v1/`, `data/output_v2/`, `data/output_v3/`:

| File | Content |
|---|---|
| `diabetes_final.xlsx` | Consolidated dataset (100,000 lines, 10 columns) |
| `diabetes_analysis.xlsx` | Sheets `technical_q1_shapes`, `technical_q5_describe`, `business_questions` and `graphs` |
| `patients_per_gender.png`, `prevalence_per_gender.png`, `age_distribution.png`, `blood_glucose_distribution.png` | The 4 graphs |

The app produces its own downloads, see [app.md](app.md).

## 6. Troubleshooting

| Problem | Cause and fix |
|---|---|
| `FileNotFoundError: data/diabetes_part1.csv` | The data is missing: see step 3. Run from the project root |
| `ModuleNotFoundError` | Dependencies not installed: `uv sync`, then use `uv run ...` (not the system Python) |
| Notebook: kernel not found | Select the interpreter `.venv/bin/python` (`.venv\Scripts\python.exe` on Windows) |
| App: the theme is not applied | Launch `streamlit run` from the project root, where `.streamlit/` is |
| App: `... is missing the columns: [...]` | A loaded part does not have the expected columns, see [data.md](data.md) |
| App: `Gender codes missing from the mapping table` | A `gender_code` of the parts is not in the mapping file |
| App: `The file ... was loaded twice` | Two uploaded parts have the same file name |
| `make: command not found` (Windows) | Use the `uv run ...` commands instead |
