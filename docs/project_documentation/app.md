# Streamlit app

File: [`app/app.py`](../../app/app.py). Assets: `app/assets/logo.svg`, `app/assets/style.css`.
Theme: `.streamlit/config.toml`.

## Run

```bash
make run_app                       # or: uv run streamlit run app/app.py
```

Run it from the project root. Streamlit opens http://localhost:8501.

## User guide

### 1. Load the files (sidebar, *Data files*)

| Field | What to load |
|---|---|
| **Check-up parts (CSV)** | One or several CSV files with the 9 check-up columns. Load as many parts as you have: 2, 3, 4... |
| **Gender mapping (CSV)** | The mapping with the columns `gender_code` and `gender` |

Until both are loaded, the app shows an invitation message. The app never reads the `data/` folder.

Errors are displayed in red instead of crashing: missing columns, a file loaded twice, gender codes absent from the
mapping, or a merge that would change the number of lines.

### 2. Filter the patients (sidebar, *Filters*)

| Filter | Type |
|---|---|
| Gender | Multi-select |
| Smoking history | Multi-select |
| Age | Range slider |

A caption shows how many patients are selected (`X of Y`). The filters apply to the **Analysis** and **Export**
tabs. **Ingestion** and **Transformation** always show the full data, because they describe the pipeline.
If no patient matches, a warning is shown.

### 3. Tabs

| Tab | Content |
|---|---|
| **Ingestion** | Lines and columns of each loaded file, and a preview of each (20 lines) |
| **Transformation** | Steps of the consolidation, quality checks, the final dataset (50 lines), numeric and text statistics |
| **Analysis** | 4 key figures, the table of business questions, 4 interactive graphs (hover for the values) |
| **Export** | 3 download buttons |

### 4. Export (downloads)

| Button | File | Content |
|---|---|---|
| Analysis report (Excel) | `diabetes_analysis.xlsx` | Sheets `shapes`, `describe`, `business_questions`, `graphs` |
| Filtered dataset (CSV) | `diabetes_final.csv` | The filtered patients, all columns |
| Graphs (PNG, zip) | `diabetes_graphs.zip` | The 4 graphs as PNG files |

The report and the graphs use the **filtered** patients. The `business_questions` sheet starts with the number of
lines of each part, the number of duplicates, and `Patients selected by the filters` (for example `18267 of 100000`).
When a group has no patient left (for example no man after filtering on women), the answer is `n/a`.

## Code reference

`app/app.py` is organised in sections.

### Ingestion and transformation

| Function | Description |
|---|---|
| `read_csv(source, required, name)` | Reads a CSV and raises `ValueError` if columns are missing |
| `load_data(part_files, mapping_file)` | Returns `({file name: DataFrame}, gender_mapping)`. Raises `ValueError` if a file is loaded twice |
| `consolidate(parts, gender_mapping)` | Concatenates the parts, merges the mapping. Raises `ValueError` on a lost line or an unmapped code |
| `quality_checks(parts, df_final)` | Table of checks displayed in the Transformation tab |

### Macro analysis

| Function | Description |
|---|---|
| `compute_shapes(datasets)` | Lines and columns of each dataset |
| `prevalence_by(df, column)` | Mean of `diabetes` per value of `column` |
| `headline_kpis(df)` | The four key figures |
| `ratio(numerator, denominator)` | Safe division, `None` if a value is missing or the denominator is 0 |
| `answer_business_questions(df)` | `{question: answer}` for the 15 business answers |
| `build_insights_table(parts, gender_mapping, df_final, df_filtered)` | The Question / Answer table (lines per file, duplicates, selection size, business answers on the filtered data) |

### Charts

| Function | Description |
|---|---|
| `bar_chart`, `histogram_by_diabetes`, `make_graphs(df)` | Static matplotlib figures, used for the exports |
| `interactive_bar_chart`, `interactive_distribution`, `make_interactive_charts(df)` | Altair charts displayed in the app |

Constants: `GENDER_COLORS` (Female pink, Male blue), `OTHER_COLOR` (grey, any other gender), `DIABETES_COLORS`
(non-diabetic teal, diabetic orange). Change a colour there and it changes in every graph.

The distributions are drawn as densities computed with `numpy.histogram`, so the diabetic group (8.5 % of the
patients) is comparable with the non-diabetic group. The chart receives about 80 points, not 100,000 lines.

### Export

| Function | Description |
|---|---|
| `figure_to_png(fig)` | Figure → PNG bytes |
| `png_file_name(title)` | `"Distribution of age"` → `distribution_of_age.png` |
| `to_csv_bytes(df)` | DataFrame → CSV bytes |
| `to_excel_bytes(df_shapes, df_describe, df_insights, graphs)` | Report as Excel bytes, in memory |
| `graphs_to_zip_bytes(graphs)` | PNG files in a zip, in memory |

### User interface

| Function | Description |
|---|---|
| `read_css(path)`, `load_style()` | Inject `style.css` (read once, cached) |
| `display_header()` | Centred title, then subtitle, description and author aligned on the left, and a divider |
| `sidebar_header()` | Logo and name |
| `choose_inputs()` | The two uploaders. Stops the script until the files are loaded |
| `apply_filters(df)` | The three filters; returns the filtered DataFrame |
| `main()` | Runs the pipeline and displays the tabs. Called at the bottom of the file |

## Customise

| I want to... | Do this |
|---|---|
| Change the logo | Replace `app/assets/logo.svg` (keep the name) |
| Change the colours of the interface | Edit `[theme]` in `.streamlit/config.toml` (separate light and dark values) |
| Change the CSS | Edit `app/assets/style.css` |
| Change the colours of the graphs | Edit the constants at the top of `app/app.py` |
| Change the description or the author | Edit `display_header()` |
| Add a business question | Add an entry in `answer_business_questions` |
| Add a filter | Add a widget and a condition on `mask` in `apply_filters` |
| Add a graph | Add a function in the charts sections and register it in `make_graphs` **and** `make_interactive_charts` (same title) |

## Limits

- Files are limited to 200 MB each (Streamlit default).
- The whole analysis is recomputed at each interaction. It takes well under a second on 100,000 lines;
  for much larger data, cache the loading with `st.cache_data`.
- The graphs of the Excel report are static images (matplotlib), the graphs on screen are interactive (Altair).
