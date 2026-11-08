TOOLS = {
    "profile_dataset": {
        "description": (
            "Analyser globalement le dataset : nombre de lignes, "
            "colonnes, types, valeurs manquantes et doublons."
        ),
        "parameters": []
    },

    "describe_column": {
        "description": (
            "Analyser une colonne de n'importe quel type : "
            "numérique, texte, catégorie, date ou identifiant. "
            "Retourne son type, ses valeurs uniques, ses valeurs "
            "manquantes et des statistiques adaptées."
        ),
        "parameters": ["column"]
    },

    "calculate_kpi": {
        "description": (
            "Calculer une statistique sur une colonne. "
            "count et nunique fonctionnent sur tous les types. "
            "sum et mean nécessitent une colonne numérique. "
            "min et max nécessitent une colonne comparable."
        ),
        "parameters": ["column", "operation"]
    },

    "aggregate_by": {
        "description": (
            "Regrouper les lignes par une colonne catégorielle, "
            "textuelle ou temporelle et calculer une statistique "
            "sur une autre colonne. count et nunique acceptent "
            "tous les types de mesures. sum et mean nécessitent "
            "une mesure numérique."
        ),
        "parameters": [
            "metric_column",
            "group_by",
            "operation"
        ]
    },

    "filter_dataset": {
        "description": (
            "Filtrer les lignes selon une condition sur une "
            "colonne numérique, textuelle, catégorielle ou date."
        ),
        "parameters": [
            "column",
            "operator",
            "value"
        ]
    },

    "create_chart": {
        "description": (
            "Créer les données nécessaires à un graphique à partir "
            "des colonnes du dataset. La colonne Y doit être "
            "numérique et la colonne X peut être de n'importe quel type."
        ),
        "parameters": [
            "chart_type",
            "x_column",
            "y_column"
        ]
    }
}


def get_tools_description():
    descriptions = []

    for tool_name, tool_info in TOOLS.items():
        descriptions.append(
            f"- {tool_name}: {tool_info['description']}"
        )
        descriptions.append(
            f"  Paramètres: {tool_info['parameters']}"
        )

    return "\n".join(descriptions)


def get_allowed_tool_names():
    return list(TOOLS.keys())