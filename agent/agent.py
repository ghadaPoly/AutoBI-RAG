import json
import re

import pandas as pd
from pandas.api.types import (
    is_numeric_dtype,
    is_datetime64_any_dtype
)

from agent.llm_client import ask_llm
from agent.dataset_context import (
    build_dataset_context,
    format_dataset_context
)
from agent.prompts import AGENT_PLANNING_PROMPT
from agent.tool_registry import (
    get_tools_description,
    get_allowed_tool_names
)
from agent.agent_config import (
    INTENTS,
    OPERATIONS,
    FILTER_OPERATORS,
    CHART_TYPES
)


# --------------------------------------------------
# 1. EXTRACTION DU JSON
# --------------------------------------------------

def extract_json(text):
    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Aucun objet JSON trouvé dans la réponse.")

    return json.loads(cleaned[start:end + 1])


# --------------------------------------------------
# 2. FONCTIONS DE VERIFICATION DES TYPES
# --------------------------------------------------

def is_numeric_column(df, column):
    return is_numeric_dtype(df[column])


def is_datetime_column(df, column):
    return is_datetime64_any_dtype(df[column])


def validate_operation(df, column, operation):
    """
    Vérifie si une opération est compatible avec une colonne.
    """

    if column not in df.columns:
        raise ValueError(f"Colonne inconnue : {column}")

    if operation not in OPERATIONS:
        raise ValueError(f"Opération non autorisée : {operation}")

    numeric = is_numeric_column(df, column)

    if operation in ["sum", "mean"] and not numeric:
        raise ValueError(
            f"L'opération {operation} nécessite une colonne numérique. "
            f"La colonne '{column}' n'est pas numérique."
        )

    if operation in ["min", "max"]:
        if not (
            numeric
            or is_datetime_column(df, column)
            or df[column].dtype == object
            or pd.api.types.is_string_dtype(df[column])
        ):
            raise ValueError(
                f"L'opération {operation} n'est pas compatible "
                f"avec la colonne '{column}'."
            )


# --------------------------------------------------
# 3. VALIDATION DU PLAN
# --------------------------------------------------

def validate_plan(plan, df):

    if not isinstance(plan, dict):
        raise ValueError("Le plan doit être un objet JSON.")

    required_keys = {
        "intent",
        "understanding",
        "columns",
        "plan",
        "needs_clarification",
        "clarification_question"
    }

    if not required_keys.issubset(plan.keys()):
        raise ValueError("Structure du plan incomplète.")

    if plan["intent"] not in INTENTS:
        raise ValueError("Intention non autorisée.")

    if not isinstance(plan["columns"], list):
        raise ValueError("Les colonnes doivent être une liste.")

    if not isinstance(plan["plan"], list):
        raise ValueError("Le plan d'exécution doit être une liste.")

    if not isinstance(plan["needs_clarification"], bool):
        raise ValueError("needs_clarification doit être booléen.")

    available_columns = set(map(str, df.columns))

    for column in plan["columns"]:
        if column not in available_columns:
            raise ValueError(
                f"Colonne inconnue dans le plan : {column}"
            )

    if plan["needs_clarification"]:
        if plan["plan"]:
            raise ValueError(
                "Un plan de clarification ne doit pas contenir d'outil."
            )
        return plan

    allowed_tools = get_allowed_tool_names()

    for step in plan["plan"]:

        if not isinstance(step, dict):
            raise ValueError("Étape invalide dans le plan.")

        tool = step.get("tool")
        parameters = step.get("parameters")

        if tool not in allowed_tools:
            raise ValueError(f"Outil non autorisé : {tool}")

        if not isinstance(parameters, dict):
            raise ValueError("Paramètres invalides.")

        if tool == "calculate_kpi":

            column = parameters.get("column")
            operation = parameters.get("operation")

            if column not in available_columns:
                raise ValueError("Colonne KPI inconnue.")

            validate_operation(df, column, operation)

        elif tool == "aggregate_by":

            metric = parameters.get("metric_column")
            group_by = parameters.get("group_by")
            operation = parameters.get("operation")

            if metric not in available_columns:
                raise ValueError("Colonne de mesure inconnue.")

            if group_by not in available_columns:
                raise ValueError("Colonne de regroupement inconnue.")

            validate_operation(df, metric, operation)

        elif tool == "describe_column":

            column = parameters.get("column")

            if column not in available_columns:
                raise ValueError("Colonne inconnue.")

        elif tool == "filter_dataset":

            column = parameters.get("column")
            operator = parameters.get("operator")

            if column not in available_columns:
                raise ValueError("Colonne de filtre inconnue.")

            if operator not in FILTER_OPERATORS:
                raise ValueError("Opérateur non autorisé.")

            if "value" not in parameters:
                raise ValueError("Valeur de filtre manquante.")

        elif tool == "create_chart":

            chart_type = parameters.get("chart_type")
            x_column = parameters.get("x_column")
            y_column = parameters.get("y_column")

            if chart_type not in CHART_TYPES:
                raise ValueError("Type de graphique non autorisé.")

            if x_column not in available_columns:
                raise ValueError("Colonne X inconnue.")

            if y_column not in available_columns:
                raise ValueError("Colonne Y inconnue.")

            if not is_numeric_column(df, y_column):
                raise ValueError(
                    "La colonne Y du graphique doit être numérique."
                )

        elif tool == "profile_dataset":

            if parameters:
                raise ValueError(
                    "profile_dataset ne prend aucun paramètre."
                )

    return plan


# --------------------------------------------------
# 4. PREPARATION DU PLAN PAR LE LLM
# --------------------------------------------------

def plan_question(df, question, dataset_name="dataset"):

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    context = build_dataset_context(
        df,
        dataset_name=dataset_name
    )

    formatted_context = format_dataset_context(context)

    tools_description = get_tools_description()

    prompt = AGENT_PLANNING_PROMPT.format(
        dataset_context=formatted_context,
        tools_description=tools_description,
        question=question
    )

    llm_response = ask_llm(prompt)

    plan = extract_json(llm_response)

    return validate_plan(plan, df)


# --------------------------------------------------
# 5. OUTIL : PROFIL DU DATASET
# --------------------------------------------------

def run_profile_dataset(df):

    return {
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "columns": list(map(str, df.columns)),
        "types": {
            str(col): str(dtype)
            for col, dtype in df.dtypes.items()
        },
        "missing_values": {
            str(col): int(value)
            for col, value in df.isna().sum().items()
        },
        "duplicate_rows": int(df.duplicated().sum())
    }


# --------------------------------------------------
# 6. OUTIL : DESCRIPTION D'UNE COLONNE
# --------------------------------------------------

def run_describe_column(df, column):

    series = df[column]

    result = {
        "column": column,
        "dtype": str(series.dtype),
        "total_rows": int(len(series)),
        "missing_values": int(series.isna().sum()),
        "unique_values": int(series.nunique()),
        "sample_values": [
            str(value)
            for value in series.dropna().head(5).tolist()
        ]
    }

    if is_numeric_column(df, column):

        result["statistics"] = {
            "mean": safe_value(series.mean()),
            "median": safe_value(series.median()),
            "min": safe_value(series.min()),
            "max": safe_value(series.max()),
            "sum": safe_value(series.sum())
        }

    else:

        result["most_frequent_values"] = {
            str(key): int(value)
            for key, value in series.value_counts().head(10).items()
        }

    if is_datetime_column(df, column):
        result["date_range"] = {
            "minimum": safe_value(series.min()),
            "maximum": safe_value(series.max())
        }

    return result


# --------------------------------------------------
# 7. OUTIL : CALCUL KPI
# --------------------------------------------------

def safe_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return str(value) if isinstance(value, pd.Timestamp) else value


def run_calculate_kpi(df, column, operation):

    validate_operation(df, column, operation)

    series = df[column]

    if operation == "sum":
        result = series.sum()

    elif operation == "mean":
        result = series.mean()

    elif operation == "count":
        result = series.count()

    elif operation == "nunique":
        result = series.nunique()

    elif operation == "min":
        result = series.min()

    elif operation == "max":
        result = series.max()

    else:
        raise ValueError("Opération non prise en charge.")

    return {
        "column": column,
        "operation": operation,
        "result": safe_value(result)
    }


# --------------------------------------------------
# 8. OUTIL : AGREGATION
# --------------------------------------------------

def run_aggregate_by(
    df,
    metric_column,
    group_by,
    operation
):

    validate_operation(df, metric_column, operation)

    if group_by not in df.columns:
        raise ValueError("Colonne de regroupement inconnue.")

    if operation == "sum":
        grouped = df.groupby(
            group_by,
            dropna=False
        )[metric_column].sum()

    elif operation == "mean":
        grouped = df.groupby(
            group_by,
            dropna=False
        )[metric_column].mean()

    elif operation == "count":
        grouped = df.groupby(
            group_by,
            dropna=False
        )[metric_column].count()

    elif operation == "nunique":
        grouped = df.groupby(
            group_by,
            dropna=False
        )[metric_column].nunique()

    elif operation == "min":
        grouped = df.groupby(
            group_by,
            dropna=False
        )[metric_column].min()

    elif operation == "max":
        grouped = df.groupby(
            group_by,
            dropna=False
        )[metric_column].max()

    else:
        raise ValueError("Opération non prise en charge.")

    return {
        "group_by": group_by,
        "metric_column": metric_column,
        "operation": operation,
        "data": [
            {
                "category": str(index),
                "value": safe_value(value)
            }
            for index, value in grouped.items()
        ]
    }


# --------------------------------------------------
# 9. OUTIL : FILTRAGE
# --------------------------------------------------

def run_filter_dataset(df, column, operator, value):

    series = df[column]

    if operator == "equals":
        mask = series.astype(str) == str(value)

    elif operator == "not_equals":
        mask = series.astype(str) != str(value)

    elif operator == "contains":
        mask = series.astype(str).str.contains(
            str(value),
            case=False,
            na=False,
            regex=False
        )

    elif operator == "greater_than":
        converted = pd.to_numeric(series, errors="coerce")
        comparison_value = pd.to_numeric(
            pd.Series([value]),
            errors="coerce"
        ).iloc[0]

        if pd.isna(comparison_value):
            raise ValueError("La valeur de comparaison doit être numérique.")

        mask = converted > comparison_value

    elif operator == "less_than":
        converted = pd.to_numeric(series, errors="coerce")
        comparison_value = pd.to_numeric(
            pd.Series([value]),
            errors="coerce"
        ).iloc[0]

        if pd.isna(comparison_value):
            raise ValueError("La valeur de comparaison doit être numérique.")

        mask = converted < comparison_value

    else:
        raise ValueError("Opérateur non autorisé.")

    filtered = df.loc[mask]

    return {
        "column": column,
        "operator": operator,
        "value": value,
        "matching_rows": int(len(filtered)),
        "data": filtered.head(100).to_dict(orient="records"),
        "truncated": len(filtered) > 100
    }


# --------------------------------------------------
# 10. OUTIL : CREATION DES DONNEES DU GRAPHIQUE
# --------------------------------------------------

def run_create_chart(
    df,
    chart_type,
    x_column,
    y_column
):

    if chart_type not in CHART_TYPES:
        raise ValueError("Type de graphique non autorisé.")

    if x_column not in df.columns or y_column not in df.columns:
        raise ValueError("Colonne de graphique inconnue.")

    if not is_numeric_column(df, y_column):
        raise ValueError("La colonne Y doit être numérique.")

    grouped = (
        df.groupby(x_column, dropna=False)[y_column]
        .sum()
        .reset_index()
    )

    return {
        "chart_type": chart_type,
        "x_column": x_column,
        "y_column": y_column,
        "data": [
            {
                "x": str(row[x_column]),
                "y": safe_value(row[y_column])
            }
            for _, row in grouped.head(500).iterrows()
        ]
    }


# --------------------------------------------------
# 11. EXECUTION SECURISEE DES OUTILS
# --------------------------------------------------

def execute_plan(df, plan):

    validated_plan = validate_plan(plan, df)

    if validated_plan["needs_clarification"]:
        return {
            "status": "clarification",
            "question": validated_plan["clarification_question"],
            "results": []
        }

    results = []

    for step in validated_plan["plan"]:

        tool = step["tool"]
        params = step["parameters"]

        if tool == "profile_dataset":
            output = run_profile_dataset(df)

        elif tool == "describe_column":
            output = run_describe_column(
                df,
                params["column"]
            )

        elif tool == "calculate_kpi":
            output = run_calculate_kpi(
                df,
                params["column"],
                params["operation"]
            )

        elif tool == "aggregate_by":
            output = run_aggregate_by(
                df,
                params["metric_column"],
                params["group_by"],
                params["operation"]
            )

        elif tool == "filter_dataset":
            output = run_filter_dataset(
                df,
                params["column"],
                params["operator"],
                params["value"]
            )

        elif tool == "create_chart":
            output = run_create_chart(
                df,
                params["chart_type"],
                params["x_column"],
                params["y_column"]
            )

        else:
            raise ValueError(f"Outil non implémenté : {tool}")

        results.append({
            "tool": tool,
            "parameters": params,
            "output": output
        })

    return {
        "status": "success",
        "understanding": validated_plan["understanding"],
        "intent": validated_plan["intent"],
        "results": results
    }


# --------------------------------------------------
# 12. FONCTION PRINCIPALE : QUESTION + EXECUTION
# --------------------------------------------------

def execute_question(df, question, dataset_name="dataset"):

    plan = plan_question(
        df=df,
        question=question,
        dataset_name=dataset_name
    )

    execution = execute_plan(df, plan)

    return {
        "plan": plan,
        "execution": execution
    }