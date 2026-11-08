import streamlit as st
import pandas as pd

from bi_engine.csv_loader import load_csv
from bi_engine.profiler import profile_dataset
from bi_engine.kpi import (
    calculate_basic_kpis,
    calculate_sales_kpis,
    aggregate_data
)
from visualization.charts import create_bar_chart


st.set_page_config(
    page_title="AutoBI-RAG",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AutoBI-RAG")
st.subheader("Intelligent Conversational Business Intelligence")

st.write(
    "Importez un fichier CSV pour analyser automatiquement "
    "sa structure, calculer des KPI et visualiser vos données."
)

uploaded_file = st.file_uploader(
    "Choisissez votre fichier CSV",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = load_csv(uploaded_file)

        st.success("Fichier importé avec succès !")

        st.header("1. Aperçu des données")
        st.dataframe(df.head(20), use_container_width=True)

        profile = profile_dataset(df)

        st.header("2. Profiling du dataset")

        col1, col2, col3 = st.columns(3)

        col1.metric("Nombre de lignes", profile["rows"])
        col2.metric("Nombre de colonnes", profile["columns"])
        col3.metric("Doublons", profile["duplicates"])

        st.write("Types des colonnes")
        st.json(profile["data_types"])

        st.write("Valeurs manquantes")
        st.json(profile["missing_values"])

        st.header("3. KPI génériques")

        basic_kpis = calculate_basic_kpis(df)

        cols = st.columns(min(4, len(basic_kpis)))

        for index, (name, value) in enumerate(basic_kpis.items()):
            cols[index % len(cols)].metric(name, value)

        sales_kpis = calculate_sales_kpis(df)

        if sales_kpis is not None:
            st.header("4. KPI commerciaux")

            cols = st.columns(len(sales_kpis))

            for index, (name, value) in enumerate(sales_kpis.items()):
                cols[index].metric(name, value)

        st.header("5. Analyse par catégorie")

        categorical_columns = profile["categorical_columns"]
        numeric_columns = profile["numeric_columns"]

        if categorical_columns and numeric_columns:

            selected_group = st.selectbox(
                "Regrouper par",
                categorical_columns
            )

            selected_value = st.selectbox(
                "Mesurer",
                numeric_columns
            )

            operation = st.selectbox(
                "Opération",
                ["sum", "mean", "count", "min", "max"]
            )

            if st.button("Générer l'analyse"):

                result = aggregate_data(
                    df,
                    selected_group,
                    selected_value,
                    operation
                )

                st.dataframe(result, use_container_width=True)

                fig = create_bar_chart(
                    result,
                    selected_group,
                    selected_value
                )

                st.plotly_chart(fig, use_container_width=True)

    except Exception as error:
        st.error(f"Erreur pendant l'analyse : {error}")