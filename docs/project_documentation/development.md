# Development

## Tooling

| Tool | Use | Command |
|---|---|---|
| uv | Environment and dependencies | `uv sync`, `uv add <package>`, `uv run <script>` |
| ruff | Lint and format | `make lint`, `make format` |
| make | Shortcuts | `make help` |
| VSCode | Editor, notebook, `# %%` cells | Extensions in `.vscode/extensions.json` |

## Commands

```text
make install     Install dependencies
make run_demo    Run the demo script
make run_v2      Run the case study, version 2 (script with cells)
make run_v3      Run the case study, version 3 (script with functions)
make run_app     Run the Streamlit app
make lint        Check code with ruff
make format      Format code with ruff
make clean       Remove caches
```

## Dependencies

Declared in `pyproject.toml`, locked in `uv.lock`.

| Package | Used for |
|---|---|
| pandas | Tables |
| matplotlib | Static graphs |
| openpyxl | Excel export, images in Excel |
| streamlit | Web app (installs altair) |
| ruff | Lint and format |
| ipykernel | Notebook kernel |
| scikit-learn | Not used yet |

Add a package: `uv add <package>`; it updates `pyproject.toml` and `uv.lock`.

## Code conventions

- Code, comments, docstrings and user interface in **English**.
- Type hints on functions, a one-line docstring on every function.
- Format with ruff before committing: `make format && make lint`.
- A bare expression at the end of a cell (`df_shapes`, `df_final.head()`) is intended, it displays the value in
  the Interactive Window: rule `B018` is ignored for `scripts/02_*.py` and `*.ipynb`.
- **Dictionary, then DataFrame**: build the tables from a named dictionary, then call `pd.DataFrame(...)`.
- Commits follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.

## Git

- Branch: `main`.
- `data/*` is git-ignored (except `data/.gitkeep`): never commit the datasets or the outputs.
- `.venv`, `__pycache__`, build files are ignored.

## Checking a change

There is no automated test suite. Check a change like this:

```bash
make lint                       # no ruff error
make run_v3                     # the pipeline runs and prints the question/answer table
make run_app                    # then load the files in the sidebar and check every tab
```

For the app, `streamlit.testing.v1.AppTest` can run the script without a browser (it cannot upload files). The
functions of `app/app.py` do not need Streamlit: a script can import them and compare their output with
version 3, for example with the 4 parts built by splitting the data.

When you change a number or a question, change it in the versions that compute it (cells, functions, app) and in
[results.md](results.md): they must stay identical.

## How to extend

| Goal | Where |
|---|---|
| New business question | `answer_business_questions` (v3 and app), new cell (v1, v2), then [results.md](results.md) |
| New data column | `PART_COLUMNS` in the app, and the analysis that uses it |
| New export format | A `to_<format>_bytes` function and a `st.download_button` in the Export tab |
| Modelling (prediction of diabetes) | `scikit-learn` is already a dependency; start from `df_final` with `diabetes` as target |
| Move the app functions into modules | Split the sections of `app/app.py` (pipeline, analysis, charts, export) into `app/*.py` files, keeping `app/app.py` for the UI |
| Tests | Add `pytest` (`uv add --dev pytest`) and test `consolidate`, `prevalence_by` and `answer_business_questions` on a small DataFrame |

## Known limitations

- The numbers in [results.md](results.md) are written by hand from the outputs: update them if the data changes.
- Versions 1-3 hard-code the file names and the two-part structure; only the app accepts any number of parts.
- `src/do_course06/` is the package created by `uv init`; it is not used by the analysis.
- The Excel sheet names differ between the scripts (`technical_q1_shapes`, `technical_q5_describe`) and the app
  (`shapes`, `describe`).
