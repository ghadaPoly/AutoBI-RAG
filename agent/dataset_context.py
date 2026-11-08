
from typing import Any
import pandas as pd


def _safe_value(value: Any) -> Any:
    """Convertit les valeurs Pandas en types sérialisables."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def build_dataset_context(
    df: pd.DataFrame,
    dataset_name: str = "dataset"
) -> dict:
    """
    Construit un contexte descriptif à partir d'un DataFrame.

    Le contexte sera transmis au LLM pour lui permettre
    de comprendre la structure du dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Le dataset doit être un DataFrame Pandas.")

    if df.empty:
        raise ValueError("Le dataset est vide.")

    columns_info = []

    for column in df.columns:
        series = df[column]

        examples = [
            _safe_value(value)
            for value in series.dropna().head(5).tolist()
        ]

        info = {
            "name": str(column),
            "dtype": str(series.dtype),
            "missing_values": int(series.isna().sum()),
            "missing_percentage": round(
                float(series.isna().mean() * 100), 2
            ),
            "unique_values": int(series.nunique()),
            "examples": examples
        }

        if pd.api.types.is_numeric_dtype(series):
            info["statistics"] = {
                "min": _safe_value(series.min()),
                "max": _safe_value(series.max()),
                "mean": _safe_value(series.mean()),
                "sum": _safe_value(series.sum())
            }

        elif pd.api.types.is_datetime64_any_dtype(series):
            info["statistics"] = {
                "min_date": _safe_value(series.min()),
                "max_date": _safe_value(series.max())
            }

        columns_info.append(info)

    context = {
        "dataset_name": dataset_name,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": columns_info,
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_bytes": int(
            df.memory_usage(deep=True).sum()
        )
    }

    return context


def format_dataset_context(context: dict) -> str:
    """
    Transforme le contexte structuré en texte lisible
    que le LLM pourra recevoir.
    """

    lines = [
        "INFORMATIONS SUR LE DATASET",
        f"Nom : {context['dataset_name']}",
        f"Nombre de lignes : {context['row_count']}",
        f"Nombre de colonnes : {context['column_count']}",
        f"Lignes dupliquées : {context['duplicate_rows']}",
        "",
        "DESCRIPTION DES COLONNES :"
    ]

    for column in context["columns"]:
        lines.append(
            f"\n- Colonne : {column['name']}"
        )
        lines.append(f"  Type : {column['dtype']}")
        lines.append(
            f"  Valeurs manquantes : {column['missing_values']}"
        )
        lines.append(
            f"  Valeurs distinctes : {column['unique_values']}"
        )
        lines.append(
            f"  Exemples : {column['examples']}"
        )

        if "statistics" in column:
            lines.append(
                f"  Statistiques : {column['statistics']}"
            )

    return "\n".join(lines)
