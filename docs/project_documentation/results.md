# Results

Analysis of the **100,000 screened patients** (2 parts of 50,000, 3 gender codes). The figures are computed by the
four versions of the project and are identical.

## Technical questions

| # | Question | Answer |
|---|---|---|
| 1 | Lines and columns | part1: 50,000 × 9; part2: 50,000 × 9; mapping: 3 × 2; **final dataset: 100,000 × 10** |
| 2 | Column names of the final dataset | `gender_code`, `age`, `hypertension`, `heart_disease`, `smoking_history`, `bmi`, `HbA1c_level`, `blood_glucose_level`, `diabetes`, `gender` |
| 3-4 | Top 5 and last 5 lines | `head()` and `tail()` in the notebook and the scripts; first 50 lines in the app |
| 5 | General statistics | `describe(include="all")` |
| 6 | Exact duplicates | **3,854 lines. Kept**: no patient identifier, identical lines can be different patients |

## Business questions

| # | Question | Answer |
|---|---|---|
| 1 | Patients screened | 100,000 |
| 2 | Diabetic patients, prevalence | 8,500, **8.5 %** |
| 3 | Prevalence for women / men | 7.6 % / 9.7 % |
| 4 | Average age, diabetic / non-diabetic | 60.9 / 40.1 years |
| 5 | Prevalence with BMI >= 30 / BMI < 30 | 18.0 % / 5.6 % |
| 6 | Average HbA1c, diabetic / non-diabetic | 6.93 % / 5.40 % |
| 6 | Average blood glucose, diabetic / non-diabetic | 194 / 133 mg/dL |
| 7 | Prevalence with hypertension vs without | **4.0 times** higher |
| 8 | Smoking history with the highest prevalence | `former` |

## Interpretation

- **Age**: diabetic patients are about 20 years older on average (60.9 vs 40.1).
- **Obesity** (BMI >= 30) multiplies the prevalence by about 3 (18.0 % vs 5.6 %).
- **Hypertension** is associated with a prevalence 4 times higher.
- **Men are more affected** than women (9.7 % vs 7.6 %).
- **The biological markers separate the two groups**: HbA1c and blood glucose are clearly higher for diabetic
  patients, as expected, since they are used to diagnose diabetes. The distributions still overlap: blood
  glucose ranges from 126 to 300 mg/dL for diabetic patients and from 80 to 200 for non-diabetic patients, so a
  single marker does not give a certain diagnosis.
- **Smoking history**: the highest prevalence is for `former` smokers, not for `current` ones. A plausible
  explanation is the age: former smokers are the oldest group (average age 57, against 44 for current smokers and
  44 for never-smokers), and age is linked to diabetes. A breakdown by age group would confirm or reject it.
  `No Info` is a category of its own, not a missing value.

These are **associations** observed in the screened population, not causes. The patients are those who came for a
check-up, so the prevalence is not the one of the general population.

## Suggestions for the prevention teams

- Target the awareness campaign at **older patients**, patients with **obesity** and patients with **hypertension**.
- Use the Streamlit app to refine: filter by gender, smoking history and age, and export the figures for the
  presentation.

## Graphs

| Graph | Reading |
|---|---|
| Number of patients per gender | 58,552 women, 41,430 men and only 18 `Other` patients (no diabetic one) |
| Prevalence of diabetes per gender | Men above women |
| Distribution of age | The diabetic curve is shifted toward the older ages |
| Distribution of blood glucose | The diabetic curve is shifted toward the high values |

Colours: pink = female, blue = male, grey = other; teal = non-diabetic, orange = diabetic.
