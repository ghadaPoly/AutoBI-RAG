
import streamlit as st
import pandas as pd

from bi_engine.csv_loader import load_csv
from bi_engine.profiler import profile_dataset
from bi_engine.kpi import calculate_basic_kpis

from visualization.charts import create_bar_chart

from agent.agent import execute_question


# ==================================================
# CONFIGURATION DE LA PAGE
# ==================================================

st.set_page_config(
    page_title="AutoBI-RAG",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AutoBI-RAG")
st.markdown(
    """
    ### Plateforme intelligente de Business Intelligence

    Importez un fichier CSV, explorez vos données et posez
    vos questions à un agent IA.
    """
)

st.divider()


# ==================================================
# 1. IMPORT DU DATASET
# ==================================================

st.sidebar.header("📁 Importation des données")

uploaded_file = st.sidebar.file_uploader(
    "Choisissez un fichier CSV",
    type=["csv"]
)

df = None
dataset_name = None
profile = None


if uploaded_file is not None:

    dataset_name = uploaded_file.name

    try:
        df = load_csv(uploaded_file)

        if df is None or df.empty:
            st.error("Le dataset est vide.")
            st.stop()

        st.success(
            f"Dataset chargé : {dataset_name}"
        )

    except Exception as error:
        st.error(
            f"Erreur lors du chargement du CSV : {error}"
        )
        st.stop()

else:
    st.info(
        "Veuillez importer un fichier CSV depuis le menu latéral."
    )
    st.stop()


# ==================================================
# 2. APERÇU DU DATASET
# ==================================================

st.header("1. Aperçu du dataset")

st.write(
    f"Nombre de lignes : **{df.shape[0]}**"
)

st.write(
    f"Nombre de colonnes : **{df.shape[1]}**"
)

st.dataframe(
    df.head(10),
    use_container_width=True
)


# ==================================================
# 3. PROFIL DU DATASET
# ==================================================

st.divider()
st.header("2. Profil du dataset")

try:

    profile = profile_dataset(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Nombre de lignes",
            df.shape[0]
        )

    with col2:
        st.metric(
            "Nombre de colonnes",
            df.shape[1]
        )

    with col3:
        st.metric(
            "Valeurs manquantes",
            int(df.isna().sum().sum())
        )

    with st.expander("Afficher les types des colonnes"):

        st.dataframe(
            pd.DataFrame({
                "Colonne": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Valeurs manquantes": df.isna().sum().values,
                "Valeurs uniques": df.nunique().values
            }),
            use_container_width=True
        )

except Exception as error:

    st.warning(
        f"Impossible de générer le profil : {error}"
    )


# ==================================================
# 4. KPI GENERAUX
# ==================================================

st.divider()
st.header("3. Indicateurs clés")

try:

    basic_kpis = calculate_basic_kpis(df)

    if basic_kpis:

        kpi_items = list(basic_kpis.items())

        columns = st.columns(
            min(4, len(kpi_items))
        )

        for index, (name, value) in enumerate(kpi_items):

            with columns[index % len(columns)]:

                st.metric(
                    label=str(name),
                    value=str(value)
                )

    else:

        st.info(
            "Aucun indicateur numérique disponible."
        )

except Exception as error:

    st.warning(
        f"Impossible de calculer les KPI : {error}"
    )


# ==================================================
# 5. EXPLORATION DES COLONNES
# ==================================================

st.divider()
st.header("4. Exploration des colonnes")

selected_column = st.selectbox(
    "Choisissez une colonne à explorer",
    options=df.columns.tolist()
)

if selected_column:

    series = df[selected_column]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Type",
            str(series.dtype)
        )

    with col2:
        st.metric(
            "Valeurs uniques",
            int(series.nunique())
        )

    with col3:
        st.metric(
            "Valeurs manquantes",
            int(series.isna().sum())
        )

    st.write("Exemples de valeurs :")

    st.write(
        series.dropna().head(10).tolist()
    )

    if pd.api.types.is_numeric_dtype(series):

        st.write("Statistiques descriptives :")

        st.write(series.describe())

    else:

        st.write("Valeurs les plus fréquentes :")

        st.write(
            series.value_counts().head(10)
        )


# ==================================================
# 6. VISUALISATION
# ==================================================

st.divider()
st.header("5. Visualisation")

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

if numeric_columns:

    categorical_columns = [
        column
        for column in df.columns
        if column not in numeric_columns
    ]

    if categorical_columns:

        selected_group = st.selectbox(
            "Choisissez une colonne de regroupement",
            categorical_columns,
            key="visual_group"
        )

        selected_value = st.selectbox(
            "Choisissez une mesure numérique",
            numeric_columns,
            key="visual_value"
        )

        try:

            chart_result = create_bar_chart(
                df,
                selected_group,
                selected_value
            )

            st.plotly_chart(
                chart_result,
                use_container_width=True
            )

        except Exception as error:

            st.warning(
                f"Impossible de créer le graphique : {error}"
            )

    else:

        st.info(
            "Aucune colonne catégorielle disponible pour le regroupement."
        )

else:

    st.info(
        "Aucune colonne numérique disponible pour créer un graphique "
        "avec une mesure."
    )


# ==================================================
# 7. ASSISTANT IA - AUTOBI-RAG
# ==================================================

st.divider()

st.header("7. Assistant IA - AutoBI-RAG")

st.markdown(
    """
    Posez une question en langage naturel.

    L'agent analyse le contexte du dataset, choisit les outils
    adaptés et exécute les analyses autorisées.
    """
)

question = st.text_area(
    "Votre question :",
    placeholder=(
        "Exemples :\n"
        "- Combien de villes différentes existe-t-il ?\n"
        "- Quelle est la moyenne de Revenue ?\n"
        "- Décris la colonne Product.\n"
        "- Quelle catégorie apparaît le plus souvent ?\n"
        "- Donne-moi un résumé du dataset."
    ),
    height=120
)

if st.button(
    "🚀 Analyser avec l'agent IA",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Veuillez saisir une question."
        )

    else:

        try:

            with st.spinner(
                "L'agent analyse votre question et exécute les outils..."
            ):

                result = execute_question(
                    df=df,
                    question=question,
                    dataset_name=dataset_name
                )

            # Compréhension de l'agent

            st.subheader("Compréhension de l'agent")

            st.write(
                result["plan"]["understanding"]
            )

            # Plan d'analyse

            st.subheader("Plan d'analyse")

            st.json(
                result["plan"]
            )

            # Résultats de l'exécution

            st.subheader("Résultats de l'analyse")

            execution = result["execution"]

            if execution["status"] == "clarification":

                st.warning(
                    execution["question"]
                )

            else:

                for index, item in enumerate(
                    execution["results"]
                ):

                    st.markdown(
                        f"### Outil : {item['tool']}"
                    )

                    st.json(
                        item["output"]
                    )

        except Exception as error:

            st.error(
                f"Erreur de l'agent : {error}"
            )

            with st.expander("Détails techniques"):

                st.exception(error)


# ==================================================
# 8. INFORMATIONS
# ==================================================

st.divider()

st.caption(
    "AutoBI-RAG | Business Intelligence assistée par IA"
)
