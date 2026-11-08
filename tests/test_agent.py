
import pandas as pd
import pytest

import agent.agent as agent_module


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Region": ["Paris", "Lyon", "Paris", "Lille"],
        "Revenue": [1200, 800, 1500, 600],
        "Quantity": [2, 1, 3, 1]
    })


def test_extract_json():
    response = """
    ```json
    {
        "intent": "dataset_overview",
        "understanding": "Décrire le dataset",
        "columns": [],
        "plan": [],
        "needs_clarification": false,
        "clarification_question": null
    }
    ```
    """

    result = agent_module.extract_json(response)

    assert result["intent"] == "dataset_overview"


def test_validate_valid_kpi_plan(sample_df):
    plan = {
        "intent": "kpi",
        "understanding": "Somme du chiffre d'affaires",
        "columns": ["Revenue"],
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

    result = agent_module.validate_plan(plan, sample_df)

    assert result["intent"] == "kpi"


def test_reject_unknown_column(sample_df):
    plan = {
        "intent": "kpi",
        "understanding": "Calculer une somme",
        "columns": ["Unknown"],
        "plan": [],
        "needs_clarification": False,
        "clarification_question": None
    }

    with pytest.raises(ValueError):
        agent_module.validate_plan(plan, sample_df)


def test_reject_unknown_tool(sample_df):
    plan = {
        "intent": "kpi",
        "understanding": "Calculer une somme",
        "columns": ["Revenue"],
        "plan": [
            {
                "tool": "execute_python",
                "parameters": {}
            }
        ],
        "needs_clarification": False,
        "clarification_question": None
    }

    with pytest.raises(ValueError):
        agent_module.validate_plan(plan, sample_df)


def test_reject_invalid_operation(sample_df):
    plan = {
        "intent": "kpi",
        "understanding": "Calculer une somme",
        "columns": ["Revenue"],
        "plan": [
            {
                "tool": "calculate_kpi",
                "parameters": {
                    "column": "Revenue",
                    "operation": "execute_code"
                }
            }
        ],
        "needs_clarification": False,
        "clarification_question": None
    }

    with pytest.raises(ValueError):
        agent_module.validate_plan(plan, sample_df)


def test_plan_question_without_api(sample_df, monkeypatch):
    fake_response = """
    {
        "intent": "aggregation",
        "understanding": "Somme du chiffre d'affaires par région",
        "columns": ["Revenue", "Region"],
        "plan": [
            {
                "tool": "aggregate_by",
                "parameters": {
                    "metric_column": "Revenue",
                    "group_by": "Region",
                    "operation": "sum"
                }
            }
        ],
        "needs_clarification": false,
        "clarification_question": null
    }
    """

    monkeypatch.setattr(
        agent_module,
        "ask_llm",
        lambda prompt: fake_response
    )

    result = agent_module.plan_question(
        sample_df,
        "Quel est le chiffre d'affaires par région ?"
    )

    assert result["intent"] == "aggregation"
    assert result["plan"][0]["tool"] == "aggregate_by"
