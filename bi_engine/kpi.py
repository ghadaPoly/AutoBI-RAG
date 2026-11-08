import pandas as pd


def calculate_basic_kpis(df):
    """
    Calcule des statistiques génériques
    à partir du dataset.
    """

    kpis = {
        "number_of_rows": int(len(df)),
        "number_of_columns": int(len(df.columns)),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }

    numeric_df = df.select_dtypes(include="number")

    for column in numeric_df.columns:
        kpis[f"{column}_mean"] = round(
            float(numeric_df[column].mean()), 2
        )

        kpis[f"{column}_sum"] = round(
            float(numeric_df[column].sum()), 2
        )

    return kpis


def calculate_sales_kpis(df):
    """
    Calcule les KPI commerciaux si les colonnes
    nécessaires existent.
    """

    required = {"quantity", "unit_price"}

    if not required.issubset(df.columns):
        return None

    quantity = pd.to_numeric(
        df["quantity"], errors="coerce"
    )

    price = pd.to_numeric(
        df["unit_price"], errors="coerce"
    )

    revenue = quantity * price

    return {
        "total_quantity": int(quantity.sum()),
        "total_revenue": round(float(revenue.sum()), 2),
        "average_unit_price": round(float(price.mean()), 2)
    }


def aggregate_data(df, group_by, value_column, operation="sum"):
    """
    Agrège une colonne numérique par catégorie.
    """

    if group_by not in df.columns:
        raise ValueError("Colonne de regroupement introuvable.")

    if value_column not in df.columns:
        raise ValueError("Colonne de valeur introuvable.")

    if not pd.api.types.is_numeric_dtype(df[value_column]):
        raise ValueError("La colonne de valeur doit être numérique.")

    allowed_operations = ["sum", "mean", "count", "min", "max"]

    if operation not in allowed_operations:
        raise ValueError("Opération non autorisée.")

    result = df.groupby(group_by)[value_column].agg(operation)

    return result.reset_index()