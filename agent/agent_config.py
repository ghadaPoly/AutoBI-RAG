INTENTS = [
    "dataset_overview",
    "column_info",
    "kpi",
    "aggregation",
    "filter",
    "visualization",
    "comparison",
    "general_question",
    "clarification"
]

# Opérations disponibles.
# count et nunique fonctionnent sur tous les types de colonnes.
OPERATIONS = [
    "sum",
    "mean",
    "count",
    "min",
    "max",
    "nunique"
]

FILTER_OPERATORS = [
    "equals",
    "not_equals",
    "greater_than",
    "less_than",
    "contains"
]

CHART_TYPES = [
    "bar",
    "line",
    "pie",
    "scatter"
]

AGENT_OUTPUT_FORMAT = {
    "intent": "kpi",
    "understanding": "Description de la demande",
    "columns": [],
    "plan": [
        {
            "tool": "calculate_kpi",
            "parameters": {
                "column": "Revenue",
                "operation": "sum"
            }
        }
    ],
    "needs_clarification": False,
    "clarification_question": None
}