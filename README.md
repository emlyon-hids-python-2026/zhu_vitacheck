# VitaCheck - Diabetes Screening

Case study of the Python Programming course (course 06, emlyon business school).

You are a data analyst at **VitaCheck**, a network of preventive health centres. Every year, thousands of
patients come for a check-up. This project automates what used to be done by hand in Excel: consolidate the
check-up files, answer the questions of the Data Team and of the Medical Team, draw the graphs and export
the insights.

The same analysis is delivered in **four versions**, from the simplest to the most complete:

| Version | Format | File | Run |
|---|---|---|---|
| 1 | Jupyter notebook | [notebooks/01_diabetes_notebook.ipynb](notebooks/01_diabetes_notebook.ipynb) | Open in VSCode, *Run All* |
| 2 | Script with `# %%` cells | [scripts/02_diabetes_cells.py](scripts/02_diabetes_cells.py) | `make run_v2` |
| 3 | Script with functions | [scripts/03_diabetes_functions.py](scripts/03_diabetes_functions.py) | `make run_v3` |
| 4 | Streamlit web app | [app/app.py](app/app.py) | `make run_app` |

## Table of contents

- [Key results](#key-results)
- [Requirements](#requirements)
- [Installation](#installation)
- [Get the data](#get-the-data)
- [Usage](#usage)
- [The pipeline](#the-pipeline)
- [The Streamlit app](#the-streamlit-app)
- [Project structure](#project-structure)
- [Development](#development)
- [Documentation](#documentation)
- [Author](#author)

## Key results

On the 100,000 screened patients:

| Question | Answer |
|---|---|
| Patients screened / diabetic | 100,000 / 8,500 |
| Prevalence of diabetes | 8.5 % |
| Prevalence for women / men | 7.6 % / 9.7 % |
| Average age, diabetic / non-diabetic | 60.9 / 40.1 years |
| Prevalence with BMI >= 30 / BMI < 30 | 18.0 % / 5.6 % |
| Average HbA1c, diabetic / non-diabetic | 6.93 % / 5.40 % |
| Average blood glucose, diabetic / non-diabetic | 194 / 133 mg/dL |
| Prevalence with hypertension vs without | 4.0 times higher |
| Smoking history with the highest prevalence | `former` |
| Exact duplicate lines (kept) | 3,854 |

See [docs/project_documentation/results.md](docs/project_documentation/results.md) for the interpretation.

## Requirements

- [uv](https://docs.astral.sh/uv/) (installs Python and the dependencies)
- Python 3.14 (pinned in `.python-version`, installed automatically by `uv`)
- [VSCode](https://code.visualstudio.com/) is recommended (notebook and `# %%` cells); the project
  recommends its extensions in `.vscode/extensions.json`

Main dependencies: `pandas`, `matplotlib`, `openpyxl`, `streamlit` (it also provides `altair`),
`ruff`, `ipykernel`, `scikit-learn`. See [pyproject.toml](pyproject.toml).

## Installation

```bash
git clone https://github.com/emlyon-hids-python-2026/do_course06.git
cd do_course06
uv sync          # or: make install
```

## Get the data

The data is **not tracked by git** (`data/*` is ignored). The 3 files must be in the `data/` folder:

| File | Content |
|---|---|
| `diabetes_part1.csv` | First half of the check-ups (50,000 lines) |
| `diabetes_part2.csv` | Second half of the check-ups (50,000 lines) |
| `gender_mapping.csv` | Mapping between `gender_code` (`F`, `M`, `O`) and `gender` |

Download them from Brightspace, or with the download script given in [docs/brief.md](docs/brief.md#3-to-download-the-data-2-options).
Details of every column: [docs/project_documentation/data.md](docs/project_documentation/data.md).

## Usage

```bash
make help      # list the available commands
```

| Command | What it does |
|---|---|
| `make install` | Install the dependencies (`uv sync`) |
| `make run_demo` | Run the demo script (`Hello, world!`) |
| `make run_v2` | Run the case study, version 2 (script with cells) |
| `make run_v3` | Run the case study, version 3 (script with functions) |
| `make run_app` | Run the Streamlit app |
| `make lint` | Check the code with ruff |
| `make format` | Format the code with ruff |
| `make clean` | Remove the caches |

Versions 1, 2 and 3 write their results in `data/output_v1/`, `data/output_v2/` and `data/output_v3/`:

- `diabetes_final.xlsx`: the consolidated dataset
- `diabetes_analysis.xlsx`: the analysis tables and the graphs
- 4 `.png` graphs

## The pipeline

```text
diabetes_part1.csv ─┐
                    ├─ concat ──> patients ─┐
diabetes_part2.csv ─┘                       ├─ merge (on gender_code) ──> final dataset ──> analysis ──> Excel
                      gender_mapping.csv ───┘
```

1. **Ingestion:** load the CSV files with `pd.read_csv`.
2. **Transformation:** concatenate the parts (`pd.concat`), then add the `gender` column with a left merge on
   `gender_code`. Two checks make sure that no line was lost and that no gender is missing.
3. **Analysis:** technical questions (shapes, columns, head/tail, statistics, duplicates) and 8 business
   questions (prevalence by gender, age, BMI, hypertension, smoking history, biological markers).
4. **Graphs:** patients per gender, prevalence per gender, distributions of age and blood glucose.
5. **Export:** one Excel file with the tables (one sheet each) and the graphs.

## The Streamlit app

```bash
make run_app       # or: uv run streamlit run app/app.py
```

Run it from the project root: Streamlit reads the theme from `.streamlit/config.toml` in the launch folder.

The app reproduces the whole pipeline on files loaded by the user:

1. In the sidebar, load **as many check-up parts as you have** (2, 3, 4...) and the gender mapping.
2. Optionally **filter** the patients by gender, smoking history and age.
3. Browse the four tabs: **Ingestion**, **Transformation**, **Analysis** (key figures, business questions,
   interactive graphs) and **Export**.
4. **Download** the Excel report, the filtered dataset (CSV) and the graphs (PNG zip).

The files are never read from `data/`: the user always loads them. Full guide: [docs/project_documentation/app.md](docs/project_documentation/app.md).

## Project structure

```text
do_course06/
├── app/
│   ├── app.py              # Streamlit app (pipeline, analysis, charts, export, UI)
│   └── assets/
│       ├── logo.svg        # Logo displayed in the sidebar
│       └── style.css       # Custom CSS
├── .streamlit/
│   └── config.toml         # Streamlit theme (light and dark)
├── data/                   # Datasets and outputs (not tracked by git)
├── docs/                   # Documentation
├── notebooks/
│   └── 01_diabetes_notebook.ipynb   # Version 1
├── scripts/
│   ├── demo.py
│   ├── 02_diabetes_cells.py         # Version 2
│   └── 03_diabetes_functions.py     # Version 3
├── src/do_course06/        # Python package (placeholder)
├── Makefile
├── pyproject.toml
└── uv.lock
```

## Development

```bash
make lint      # ruff check
make format    # ruff format
```

- Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) style
  (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`).
- Bare expressions at the end of a cell are allowed in the notebook and in `scripts/02_*.py`: they display
  the value in the Interactive Window (rule `B018` ignored in `pyproject.toml`).

More in [docs/project_documentation/development.md](docs/project_documentation/development.md).

## Documentation

| Document | Content |
|---|---|
| [docs/project_documentation/index.md](docs/project_documentation/index.md) | Overview and reading guide |
| [docs/project_documentation/getting-started.md](docs/project_documentation/getting-started.md) | Installation, data, first run, troubleshooting |
| [docs/project_documentation/data.md](docs/project_documentation/data.md) | Datasets, data dictionary, quality checks |
| [docs/project_documentation/architecture.md](docs/project_documentation/architecture.md) | Pipeline, the four versions, design decisions |
| [docs/project_documentation/app.md](docs/project_documentation/app.md) | Streamlit app: user guide and function reference |
| [docs/project_documentation/results.md](docs/project_documentation/results.md) | Answers to the questions and interpretation |
| [docs/project_documentation/development.md](docs/project_documentation/development.md) | Tooling, conventions, how to extend the project |
| [docs/brief.md](docs/brief.md) | Original case study brief |

## Author

ZHU Lingxuan - [lingxuan.zhu@edu.em-lyon.com]
#   z h u _ v i t a c h e c k  
 