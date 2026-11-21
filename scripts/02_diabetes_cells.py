# %% [markdown]
# # VitaCheck - Diabetes Screening (version 2: script with cells)
#
# Same code as `notebooks/01_diabetes_notebook.ipynb`, but in a `.py` file.
#
# - In VSCode, click **Run Cell** above each `# %%` to run it in the Interactive Window.
# - In a terminal, run the whole script: `uv run scripts/02_diabetes_cells.py`

# %% Imports
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from openpyxl.drawing.image import Image

# %% Paths
# Works from the project root (uv run) and from scripts/ or notebooks/ (Interactive Window)
ROOT = Path.cwd() if (Path.cwd() / "data").is_dir() else Path.cwd().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = DATA_DIR / "output_v2"
OUTPUT_DIR.mkdir(exist_ok=True)

# %% [markdown]
# ## Objective 1: Automate the consolidation process

# %% Load the data
part1 = pd.read_csv(DATA_DIR / "diabetes_part1.csv")
part2 = pd.read_csv(DATA_DIR / "diabetes_part2.csv")
gender_mapping = pd.read_csv(DATA_DIR / "gender_mapping.csv")
gender_mapping

# %% Concatenation: stack part1 and part2 vertically
patients = pd.concat([part1, part2], ignore_index=True)
print(f"part1: {len(part1)} + part2: {len(part2)} = patients: {len(patients)}")

# %% Merge: add the gender column from the mapping table
df_final = patients.merge(gender_mapping, on="gender_code", how="left")

# Sanity checks: no line lost, no unknown gender code
assert len(df_final) == len(patients), "The merge changed the number of lines"
assert df_final["gender"].notna().all(), (
    "Some gender codes are not in the mapping table"
)
df_final.head()

# %% Export the final dataset to Excel
df_final.to_excel(OUTPUT_DIR / "diabetes_final.xlsx", index=False)

# %% [markdown]
# ## Objective 2: Answer some questions
#
# ### Technical questions from the Data Team

# %% Q1. Number of lines and columns
shapes = {
    "dataset": [
        "diabetes_part1.csv",
        "diabetes_part2.csv",
        "gender_mapping.csv",
        "final dataset",
    ],
    "nb_lines": [
        part1.shape[0],
        part2.shape[0],
        gender_mapping.shape[0],
        df_final.shape[0],
    ],
    "nb_columns": [
        part1.shape[1],
        part2.shape[1],
        gender_mapping.shape[1],
        df_final.shape[1],
    ],
}
df_shapes = pd.DataFrame(shapes)
df_shapes

# %% Q2. Column names
list(df_final.columns)

# %% Q3. Top 5 lines
df_final.head(5)

# %% Q4. Last 5 lines
df_final.tail(5)

# %% Q5. General statistical description (numeric and text columns)
df_describe = df_final.describe(include="all")
df_describe

# %% Q6. Exact duplicates
nb_duplicates = df_final.duplicated().sum()
print(f"{nb_duplicates} lines are exact duplicates")

# %% [markdown]
# We **keep** the duplicates: there is no patient identifier, so two different patients
# can have exactly the same profile (same gender, age, BMI, ...). Removing them would
# under-estimate the number of patients.

# %% [markdown]
# ### Business questions from the Medical Team

# %% Q1. Number of patients
nb_patients = len(df_final)
nb_patients

# %% Q2. Number of diabetic patients and prevalence
# diabetes is coded 0 / 1, so the sum counts the diabetics and the mean is the prevalence
nb_diabetic = df_final["diabetes"].sum()
prevalence = df_final["diabetes"].mean()
print(f"{nb_diabetic} diabetic patients, prevalence = {prevalence:.1%}")

# %% Q3. Prevalence for women and for men
prevalence_by_gender = df_final.groupby("gender")["diabetes"].mean()
prevalence_women = prevalence_by_gender["Female"]
prevalence_men = prevalence_by_gender["Male"]
prevalence_by_gender

# %% Q4. Average age of diabetic vs non-diabetic patients
age_by_diabetes = df_final.groupby("diabetes")["age"].mean()
age_diabetic = age_by_diabetes[1]
age_non_diabetic = age_by_diabetes[0]
age_by_diabetes

# %% Q5. Prevalence for obese patients (BMI >= 30) vs others
is_obese = df_final["bmi"] >= 30
prevalence_obese = df_final.loc[is_obese, "diabetes"].mean()
prevalence_not_obese = df_final.loc[~is_obese, "diabetes"].mean()
print(f"BMI >= 30: {prevalence_obese:.1%} | BMI < 30: {prevalence_not_obese:.1%}")

# %% Q6. Average biological markers of diabetic vs non-diabetic patients
markers_by_diabetes = df_final.groupby("diabetes")[
    ["HbA1c_level", "blood_glucose_level"]
].mean()
markers_by_diabetes

# %% Q7. Effect of hypertension
prevalence_by_hypertension = df_final.groupby("hypertension")["diabetes"].mean()
ratio_hypertension = prevalence_by_hypertension[1] / prevalence_by_hypertension[0]
print(f"The prevalence is {ratio_hypertension:.1f} times higher with hypertension")

# %% Q8. Smoking history with the highest prevalence
prevalence_by_smoking = (
    df_final.groupby("smoking_history")["diabetes"].mean().sort_values(ascending=False)
)
top_smoking_category = prevalence_by_smoking.index[0]
prevalence_by_smoking

# %% [markdown]
# `former` smokers have the highest prevalence, not `current` smokers. A likely reason:
# former smokers are older on average, and age is a strong risk factor.

# %% [markdown]
# ## Objective 3: Graph analysis

# %% Number of patients per gender
fig, ax = plt.subplots()
df_final["gender"].value_counts().plot.bar(
    ax=ax, title="Number of patients per gender", rot=0
)
fig.savefig(OUTPUT_DIR / "patients_per_gender.png", bbox_inches="tight")

# %% Prevalence of diabetes per gender
fig, ax = plt.subplots()
prevalence_by_gender.plot.bar(ax=ax, title="Prevalence of diabetes per gender", rot=0)
fig.savefig(OUTPUT_DIR / "prevalence_per_gender.png", bbox_inches="tight")

# %% Distribution of age: diabetic vs non-diabetic
fig, ax = plt.subplots()
df_final.groupby("diabetes")["age"].plot.hist(
    ax=ax, bins=40, alpha=0.5, density=True, legend=True
)
ax.set_title("Distribution of age (0 = non-diabetic, 1 = diabetic)")
fig.savefig(OUTPUT_DIR / "age_distribution.png", bbox_inches="tight")

# %% Distribution of blood glucose: diabetic vs non-diabetic
fig, ax = plt.subplots()
df_final.groupby("diabetes")["blood_glucose_level"].plot.hist(
    ax=ax, bins=40, alpha=0.5, density=True, legend=True
)
ax.set_title("Distribution of blood glucose level (0 = non-diabetic, 1 = diabetic)")
fig.savefig(OUTPUT_DIR / "blood_glucose_distribution.png", bbox_inches="tight")

# %% [markdown]
# ## Objective 4: Export the analysis

# %% Store the answers in a dictionary, then a DataFrame
dict_analysis = {
    "How many lines are in diabetes_part1.csv": len(part1),
    "How many lines are in diabetes_part2.csv": len(part2),
    "How many lines are in gender_mapping.csv": len(gender_mapping),
    "How many lines are exact duplicates": nb_duplicates,
    "How many patients were screened": nb_patients,
    "How many patients are diabetic": nb_diabetic,
    "What is the prevalence of diabetes": prevalence,
    "What is the prevalence of diabetes for women": prevalence_women,
    "What is the prevalence of diabetes for men": prevalence_men,
    "What is the average age of diabetic patients": age_diabetic,
    "What is the average age of non-diabetic patients": age_non_diabetic,
    "What is the prevalence of diabetes for patients with BMI >= 30": prevalence_obese,
    "What is the prevalence of diabetes for patients with BMI < 30": prevalence_not_obese,
    "What is the average HbA1c_level of diabetic patients": markers_by_diabetes.loc[
        1, "HbA1c_level"
    ],
    "What is the average HbA1c_level of non-diabetic patients": markers_by_diabetes.loc[
        0, "HbA1c_level"
    ],
    "What is the average blood_glucose_level of diabetic patients": markers_by_diabetes.loc[
        1, "blood_glucose_level"
    ],
    "What is the average blood_glucose_level of non-diabetic patients": markers_by_diabetes.loc[
        0, "blood_glucose_level"
    ],
    "How many times higher is the prevalence with hypertension": ratio_hypertension,
    "Which smoking_history category has the highest prevalence": top_smoking_category,
}
df_analysis = pd.DataFrame(list(dict_analysis.items()), columns=["Question", "Answer"])
df_analysis

# %% Export the tables and the graphs into one Excel file, one sheet each
graphs = [
    "patients_per_gender",
    "prevalence_per_gender",
    "age_distribution",
    "blood_glucose_distribution",
]

with pd.ExcelWriter(OUTPUT_DIR / "diabetes_analysis.xlsx") as writer:
    df_shapes.to_excel(writer, sheet_name="technical_q1_shapes", index=False)
    df_describe.to_excel(writer, sheet_name="technical_q5_describe")
    df_analysis.to_excel(writer, sheet_name="business_questions", index=False)

    sheet = writer.book.create_sheet("graphs")
    for i, name in enumerate(graphs):
        sheet.add_image(Image(OUTPUT_DIR / f"{name}.png"), f"A{1 + 25 * i}")

print(f"Analysis exported to {OUTPUT_DIR}")
