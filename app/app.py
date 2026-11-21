"""VitaCheck - Diabetes Screening: Streamlit app.

Reproduces the whole pipeline (ingestion, transformation, macro analysis)
and lets the user export the insights.

Run it from the project root:

    uv run streamlit run app/app.py
"""

import io
import re
import zipfile
from pathlib import Path
from typing import IO

import altair as alt
import matplotlib

matplotlib.use("Agg")  # no GUI backend: the figures are rendered by Streamlit

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.figure import Figure
from openpyxl.drawing.image import Image

PART_COLUMNS = {
    "gender_code",
    "age",
    "hypertension",
    "heart_disease",
    "smoking_history",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level",
    "diabetes",
}
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
MAPPING_COLUMNS = {"gender_code", "gender"}

Source = IO[bytes]

# Colours of the graphs
GENDER_COLORS = {"Female": "#ec4899", "Male": "#3b82f6"}  # pink, blue
OTHER_COLOR = "#9ca3af"  # grey, for any other gender
DIABETES_COLORS = {"non-diabetic": "#14b8a6", "diabetic": "#f97316"}  # teal, orange


# --- Ingestion and transformation ----------------------------------------------


def read_csv(source: Source, required: set[str], name: str) -> pd.DataFrame:
    """Read a CSV file and check that it contains the expected columns."""
    df = pd.read_csv(source)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} is missing the columns: {sorted(missing)}")
    return df


def load_data(
    part_files: list[Source], mapping_file: Source
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Ingestion: load any number of check-up parts and the gender mapping table.

    The parts are returned in a dictionary {file name: DataFrame}.
    """
    parts = {}
    for file in part_files:
        name = getattr(file, "name", "part")
        if name in parts:
            raise ValueError(f"The file {name} was loaded twice")
        parts[name] = read_csv(file, PART_COLUMNS, name)
    gender_mapping = read_csv(mapping_file, MAPPING_COLUMNS, "gender mapping")
    return parts, gender_mapping


def consolidate(
    parts: dict[str, pd.DataFrame], gender_mapping: pd.DataFrame
) -> pd.DataFrame:
    """Transformation: concatenate the parts, then merge the gender mapping table."""
    patients = pd.concat(parts.values(), ignore_index=True)
    df_final = patients.merge(gender_mapping, on="gender_code", how="left")

    if len(df_final) != len(patients):
        raise ValueError(
            "The merge changed the number of lines: "
            "gender_code must be unique in the mapping table"
        )
    unmapped = df_final.loc[df_final["gender"].isna(), "gender_code"].unique()
    if len(unmapped) > 0:
        raise ValueError(
            f"Gender codes missing from the mapping table: {list(unmapped)}"
        )
    return df_final


def quality_checks(
    parts: dict[str, pd.DataFrame], df_final: pd.DataFrame
) -> pd.DataFrame:
    """Return a table of checks proving that the consolidation is correct."""
    same_length = len(df_final) == sum(len(df) for df in parts.values())
    checks = {
        "Check": [
            "Lines after concatenation = sum of the parts",
            "Lines unchanged by the gender merge",
            "Every patient has a gender",
            "Missing values in the final dataset",
        ],
        "Result": [
            same_length,
            same_length,
            bool(df_final["gender"].notna().all()),
            int(df_final.isna().sum().sum()),
        ],
    }
    return pd.DataFrame(checks).astype({"Result": str})


# --- Macro analysis ------------------------------------------------------------


def compute_shapes(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Number of lines and columns of each dataset."""
    shapes = {
        "dataset": list(datasets),
        "nb_lines": [df.shape[0] for df in datasets.values()],
        "nb_columns": [df.shape[1] for df in datasets.values()],
    }
    return pd.DataFrame(shapes)


def prevalence_by(df: pd.DataFrame, column: str) -> pd.Series:
    """Prevalence of diabetes (mean of the 0/1 `diabetes` column) for each value of `column`."""
    return df.groupby(column)["diabetes"].mean()


def headline_kpis(df: pd.DataFrame) -> dict[str, float]:
    """The key figures displayed at the top of the analysis page."""
    return {
        "Patients screened": len(df),
        "Diabetic patients": int(df["diabetes"].sum()),
        "Prevalence of diabetes": df["diabetes"].mean(),
        "Average age": df["age"].mean(),
    }


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    """Ratio of two values, None when one is missing (e.g. a group filtered out) or zero."""
    if numerator is None or not denominator:
        return None
    return numerator / denominator


def answer_business_questions(df: pd.DataFrame) -> dict[str, object]:
    """Return a dictionary {question: answer} for the business questions."""
    by_gender = prevalence_by(df, "gender")
    age_by_diabetes = df.groupby("diabetes")["age"].mean()
    markers = df.groupby("diabetes")[["HbA1c_level", "blood_glucose_level"]].mean()
    by_hypertension = prevalence_by(df, "hypertension")
    by_smoking = prevalence_by(df, "smoking_history").sort_values(ascending=False)
    is_obese = df["bmi"] >= 30

    return {
        "How many patients were screened": len(df),
        "How many patients are diabetic": int(df["diabetes"].sum()),
        "What is the prevalence of diabetes": df["diabetes"].mean(),
        "What is the prevalence of diabetes for women": by_gender.get("Female"),
        "What is the prevalence of diabetes for men": by_gender.get("Male"),
        "What is the average age of diabetic patients": age_by_diabetes.get(1),
        "What is the average age of non-diabetic patients": age_by_diabetes.get(0),
        "What is the prevalence of diabetes for patients with BMI >= 30": df.loc[
            is_obese, "diabetes"
        ].mean(),
        "What is the prevalence of diabetes for patients with BMI < 30": df.loc[
            ~is_obese, "diabetes"
        ].mean(),
        "What is the average HbA1c_level of diabetic patients": markers[
            "HbA1c_level"
        ].get(1),
        "What is the average HbA1c_level of non-diabetic patients": markers[
            "HbA1c_level"
        ].get(0),
        "What is the average blood_glucose_level of diabetic patients": markers[
            "blood_glucose_level"
        ].get(1),
        "What is the average blood_glucose_level of non-diabetic patients": markers[
            "blood_glucose_level"
        ].get(0),
        "How many times higher is the prevalence with hypertension": ratio(
            by_hypertension.get(1), by_hypertension.get(0)
        ),
        "Which smoking_history category has the highest prevalence": by_smoking.index[
            0
        ],
    }


def build_insights_table(
    parts: dict[str, pd.DataFrame],
    gender_mapping: pd.DataFrame,
    df_final: pd.DataFrame,
    df_filtered: pd.DataFrame,
) -> pd.DataFrame:
    """Question / Answer table: dataset sizes, then business questions on the filtered data."""
    # Duplicates are kept: without a patient identifier, two patients can share the same profile
    answers = {
        **{f"How many lines are in {name}": len(df) for name, df in parts.items()},
        "How many lines are in the gender mapping": len(gender_mapping),
        "How many lines are exact duplicates": int(df_final.duplicated().sum()),
        "Patients selected by the filters": f"{len(df_filtered)} of {len(df_final)}",
        **answer_business_questions(df_filtered),
    }
    table = pd.DataFrame(list(answers.items()), columns=["Question", "Answer"])
    # "n/a" when a group is filtered out (e.g. no man left after filtering on women)
    table["Answer"] = table["Answer"].astype(str).fillna("n/a")
    return table


# --- Charts --------------------------------------------------------------------


def bar_chart(series: pd.Series, title: str) -> Figure:
    """Bar chart of a series indexed by gender: pink for women, blue for men."""
    fig, ax = plt.subplots()
    colors = [GENDER_COLORS.get(category, OTHER_COLOR) for category in series.index]
    series.plot.bar(ax=ax, title=title, rot=0, color=colors)
    return fig


def histogram_by_diabetes(df: pd.DataFrame, column: str, title: str) -> Figure:
    """Distribution of `column` for non-diabetic and diabetic patients."""
    fig, ax = plt.subplots()
    for value, label in [(0, "non-diabetic"), (1, "diabetic")]:
        ax.hist(
            df.loc[df["diabetes"] == value, column],
            bins=40,
            alpha=0.5,
            density=True,
            label=label,
            color=DIABETES_COLORS[label],
        )
    ax.set_title(title)
    ax.legend()
    return fig


def make_graphs(df: pd.DataFrame) -> dict[str, Figure]:
    """Create the graphs of the analysis, keyed by title."""
    return {
        "Number of patients per gender": bar_chart(
            df["gender"].value_counts(), "Number of patients per gender"
        ),
        "Prevalence of diabetes per gender": bar_chart(
            prevalence_by(df, "gender"), "Prevalence of diabetes per gender"
        ),
        "Distribution of age": histogram_by_diabetes(df, "age", "Distribution of age"),
        "Distribution of blood glucose level": histogram_by_diabetes(
            df, "blood_glucose_level", "Distribution of blood glucose level"
        ),
    }


def interactive_bar_chart(
    series: pd.Series, title: str, value_format: str = ",d"
) -> alt.Chart:
    """Interactive bar chart (tooltip on hover) of a series indexed by gender."""
    data = series.rename("value").rename_axis("category").reset_index()
    categories = list(data["category"])
    colors = [GENDER_COLORS.get(category, OTHER_COLOR) for category in categories]
    return (
        alt.Chart(data, title=title)
        .mark_bar()
        .encode(
            x=alt.X("category:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("value:Q", title=None, axis=alt.Axis(format=value_format)),
            color=alt.Color(
                "category:N",
                scale=alt.Scale(domain=categories, range=colors),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("value:Q", title="Value", format=value_format),
            ],
        )
    )


def interactive_distribution(df: pd.DataFrame, column: str, title: str) -> alt.Chart:
    """Interactive distribution of `column` for non-diabetic and diabetic patients."""
    edges = np.histogram_bin_edges(df[column], bins=40)
    frames = []
    for value, label in [(0, "non-diabetic"), (1, "diabetic")]:
        density, _ = np.histogram(
            df.loc[df["diabetes"] == value, column], bins=edges, density=True
        )
        frames.append(
            pd.DataFrame(
                {
                    column: (edges[:-1] + edges[1:]) / 2,
                    "density": density,
                    "patients": label,
                }
            )
        )
    return (
        alt.Chart(pd.concat(frames), title=title)
        .mark_area(opacity=0.5, interpolate="step")
        .encode(
            x=alt.X(f"{column}:Q"),
            y=alt.Y("density:Q", stack=None),
            color=alt.Color(
                "patients:N",
                title=None,
                scale=alt.Scale(
                    domain=list(DIABETES_COLORS), range=list(DIABETES_COLORS.values())
                ),
            ),
            tooltip=[
                alt.Tooltip(f"{column}:Q", format=".1f"),
                alt.Tooltip("density:Q", format=".4f"),
                alt.Tooltip("patients:N"),
            ],
        )
    )


def make_interactive_charts(df: pd.DataFrame) -> dict[str, alt.Chart]:
    """Interactive version of the graphs, displayed in the app, keyed by title."""
    return {
        "Number of patients per gender": interactive_bar_chart(
            df["gender"].value_counts(), "Number of patients per gender"
        ),
        "Prevalence of diabetes per gender": interactive_bar_chart(
            prevalence_by(df, "gender"), "Prevalence of diabetes per gender", ".1%"
        ),
        "Distribution of age": interactive_distribution(
            df, "age", "Distribution of age"
        ),
        "Distribution of blood glucose level": interactive_distribution(
            df, "blood_glucose_level", "Distribution of blood glucose level"
        ),
    }


# --- Export --------------------------------------------------------------------


def figure_to_png(fig: Figure) -> bytes:
    """Render a figure as PNG bytes."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    return buffer.getvalue()


def png_file_name(title: str) -> str:
    """File name of a graph, built from its title."""
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") + ".png"


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """The final dataset as CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(
    df_shapes: pd.DataFrame,
    df_describe: pd.DataFrame,
    df_insights: pd.DataFrame,
    graphs: dict[str, Figure],
) -> bytes:
    """The analysis report as Excel bytes: one sheet per table, plus a sheet of graphs."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_shapes.to_excel(writer, sheet_name="shapes", index=False)
        df_describe.to_excel(writer, sheet_name="describe")
        df_insights.to_excel(writer, sheet_name="business_questions", index=False)

        sheet = writer.book.create_sheet("graphs")
        for i, fig in enumerate(graphs.values()):
            sheet.add_image(Image(io.BytesIO(figure_to_png(fig))), f"A{1 + 25 * i}")
    return buffer.getvalue()


def graphs_to_zip_bytes(graphs: dict[str, Figure]) -> bytes:
    """All the graphs as PNG files in a zip archive."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for title, fig in graphs.items():
            archive.writestr(png_file_name(title), figure_to_png(fig))
    return buffer.getvalue()


# --- User interface ------------------------------------------------------------


@st.cache_data(show_spinner=False)
def read_css(path: Path) -> str:
    """Read the CSS file (cached: no disk access on every rerun)."""
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_style() -> None:
    """Inject the custom CSS of the app."""
    css = read_css(ASSETS_DIR / "style.css")
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def display_header() -> None:
    """Centered title, then subtitle, description and author aligned on the left."""
    st.title("VitaCheck - Diabetes Screening")
    st.markdown(
        """
        <div class="app-description">
            <p class="app-subtitle">Ingestion → Transformation → Analysis → Export</p>
            <p class="app-text">
                VitaCheck turns the raw diabetes check-up files into insights.
                Load the check-up parts and the gender mapping, and the app consolidates
                them, answers the key business questions (prevalence by gender, age,
                BMI, hypertension, smoking history...), draws interactive graphs and
                lets you filter the patients and export the results.
            </p>
            <p class="app-author">
                Author: Constance de Taillac ·
                <a href="mailto:constance.bartouilh@edu.em-lyon.com">constance.bartouilh@edu.em-lyon.com</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()


def sidebar_header() -> None:
    """Sidebar: company logo and name."""
    with st.sidebar:
        logo_column, name_column = st.columns([1, 3], vertical_alignment="center")
        logo_column.image(str(ASSETS_DIR / "logo.svg"), width=48)
        name_column.markdown("**VitaCheck**  \nDiabetes Screening")
        st.divider()


def choose_inputs() -> tuple[list[Source], Source]:
    """Sidebar: the user loads the files here, whatever the number of parts."""
    st.sidebar.header("📁 Data files")
    part_files = st.sidebar.file_uploader(
        "Check-up parts (CSV): load as many as you have",
        type="csv",
        accept_multiple_files=True,
    )
    mapping_file = st.sidebar.file_uploader("Gender mapping (CSV)", type="csv")
    if not part_files or not mapping_file:
        st.info(
            "Load the check-up parts and the gender mapping in the sidebar to start."
        )
        st.stop()
    return part_files, mapping_file


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Sidebar: filter the patients. The analysis and the export use the filtered data."""
    st.sidebar.header("🔎 Filters")
    genders = sorted(df["gender"].unique())
    smoking = sorted(df["smoking_history"].unique())
    selected_genders = st.sidebar.multiselect("Gender", genders, default=genders)
    selected_smoking = st.sidebar.multiselect(
        "Smoking history", smoking, default=smoking
    )

    mask = df["gender"].isin(selected_genders) & df["smoking_history"].isin(
        selected_smoking
    )
    age_min, age_max = int(df["age"].min()), int(df["age"].max()) + 1
    if age_min < age_max:
        low, high = st.sidebar.slider("Age", age_min, age_max, (age_min, age_max))
        mask &= df["age"].between(low, high)

    filtered = df[mask]
    st.sidebar.caption(f"{len(filtered):,} of {len(df):,} patients selected")
    return filtered


def main() -> None:
    """Run the pipeline and display the four tabs."""
    st.set_page_config(
        page_title="VitaCheck - Diabetes Screening", page_icon="🩺", layout="wide"
    )
    load_style()
    display_header()

    sidebar_header()
    try:
        parts, gender_mapping = load_data(*choose_inputs())
        df_final = consolidate(parts, gender_mapping)
    except ValueError as error:
        st.error(f"Could not run the pipeline: {error}")
        st.stop()

    datasets = {**parts, "gender mapping": gender_mapping}
    df_filtered = apply_filters(df_final)
    if df_filtered.empty:
        st.warning("No patient matches the filters: widen the selection.")
        st.stop()

    df_shapes = compute_shapes(
        {**datasets, "final dataset": df_final, "filtered dataset": df_filtered}
    )
    df_describe = df_filtered.describe(include="all")
    df_insights = build_insights_table(parts, gender_mapping, df_final, df_filtered)

    tab_ingest, tab_transform, tab_analysis, tab_export = st.tabs(
        ["📥 1. Ingestion", "🔄 2. Transformation", "📊 3. Analysis", "📤 4. Export"]
    )

    with tab_ingest:
        st.subheader("🗂️ Raw files")
        st.dataframe(df_shapes.iloc[: len(datasets)], hide_index=True)
        for name, df in datasets.items():
            with st.expander(f"{name} ({df.shape[0]} lines)"):
                st.dataframe(df.head(20))

    with tab_transform:
        st.subheader("🧩 Consolidation")
        st.markdown(
            f"1. Concatenate the {len(parts)} check-up parts\n"
            "2. Left-merge the gender mapping on `gender_code`"
        )
        st.dataframe(quality_checks(parts, df_final), hide_index=True)
        st.write(
            f"Final dataset: {df_final.shape[0]} lines, {df_final.shape[1]} columns"
        )
        st.dataframe(df_final.head(50))
        st.subheader("📈 Summary statistics")
        st.dataframe(df_final.describe())
        st.dataframe(df_final.describe(include=["str"]).astype(str))

    with tab_analysis:
        kpis = headline_kpis(df_filtered)
        cols = st.columns(len(kpis))
        cols[0].metric(
            "Patients screened", f"{kpis['Patients screened']:,}", border=True
        )
        cols[1].metric(
            "Diabetic patients", f"{kpis['Diabetic patients']:,}", border=True
        )
        cols[2].metric(
            "Prevalence of diabetes",
            f"{kpis['Prevalence of diabetes']:.1%}",
            border=True,
        )
        cols[3].metric("Average age", f"{kpis['Average age']:.1f}", border=True)

        st.subheader("💼 Business questions")
        st.dataframe(df_insights, hide_index=True, width="stretch")

        st.subheader("📉 Graphs")
        left, right = st.columns(2)
        for i, chart in enumerate(make_interactive_charts(df_filtered).values()):
            (left if i % 2 == 0 else right).altair_chart(chart, width="stretch")

    with tab_export:
        st.subheader("⬇️ Download the insights")
        st.caption(
            f"The report and the graphs use the {len(df_filtered):,} filtered patients."
        )
        graphs = make_graphs(df_filtered)
        st.download_button(
            "Analysis report (Excel)",
            to_excel_bytes(df_shapes, df_describe, df_insights, graphs),
            file_name="diabetes_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
            "Filtered dataset (CSV)",
            to_csv_bytes(df_filtered),
            file_name="diabetes_final.csv",
            mime="text/csv",
        )
        st.download_button(
            "Graphs (PNG, zip)",
            graphs_to_zip_bytes(graphs),
            file_name="diabetes_graphs.zip",
            mime="application/zip",
        )
    plt.close("all")


main()
