# VitaCheck - Diabetes Screening: documentation

This documentation describes the Python project built for the **diabetes screening case study** of the
Python Programming course (course 06, emlyon business school).

## What the project does

VitaCheck is a network of preventive health centres. Each centre sends its check-up results in separate files.
The project replaces the manual consolidation in Excel by a reproducible Python pipeline:

1. **Ingest** the check-up files and the gender mapping table
2. **Transform** them into one consolidated dataset, with checks
3. **Analyse** the dataset: technical questions and business questions about the prevalence of diabetes
4. **Export** the tables and the graphs to Excel

The pipeline exists in four versions (notebook, script with cells, script with functions, Streamlit app).
See [architecture](architecture.md).

## Reading guide

| If you want to... | Read |
|---|---|
| Install and run the project | [getting-started.md](getting-started.md) |
| Understand the datasets and the columns | [data.md](data.md) |
| Understand how the project is organised and why | [architecture.md](architecture.md) |
| Use the web app or change its code | [app.md](app.md) |
| Read the answers and their interpretation | [results.md](results.md) |
| Contribute, lint, extend | [development.md](development.md) |
| Read the original assignment | [brief.md](../brief.md) |

## Glossary

| Term | Definition |
|---|---|
| **Prevalence** | Share of patients who are diabetic: `diabetic patients / patients`. As `diabetes` is coded 0/1, it is the **mean** of the column |
| **HbA1c** | Average blood sugar level over the last 2-3 months, in % |
| **Blood glucose** | Blood sugar at the time of the check-up, in mg/dL |
| **BMI** | Body Mass Index: weight (kg) / height (m)². Obesity: BMI >= 30 |
| **Concatenation** | Stacking tables with the same columns on top of each other (`pd.concat`) |
| **Merge** | Adding the columns of another table through a common key (`DataFrame.merge`) |
| **Part** | One of the files containing a share of the check-ups (`diabetes_part1.csv`, ...) |
