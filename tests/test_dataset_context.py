
import pandas as pd

from agent.dataset_context import (
    build_dataset_context,
    format_dataset_context
)


def test_build_dataset_context():
    df = pd.DataFrame({
        "Product": ["Laptop", "Phone", "Laptop"],
        "Quantity": [2, 3, 1],
        "Unit_Price": [800, 500, 800]
    })

    context = build_dataset_context(
        df,
        dataset_name="sales.csv"
    )

    assert context["dataset_name"] == "sales.csv"
    assert context["row_count"] == 3
    assert context["column_count"] == 3
    assert len(context["columns"]) == 3
    assert context["duplicate_rows"] == 0


def test_numeric_statistics():
    df = pd.DataFrame({
        "Revenue": [100, 200, 300]
    })

    context = build_dataset_context(df)

    revenue = context["columns"][0]

    assert revenue["statistics"]["min"] == 100
    assert revenue["statistics"]["max"] == 300
    assert revenue["statistics"]["sum"] == 600


def test_missing_values():
    df = pd.DataFrame({
        "Name": ["Ali", None, "Sara"]
    })

    context = build_dataset_context(df)

    name = context["columns"][0]

    assert name["missing_values"] == 1


def test_format_context():
    df = pd.DataFrame({
        "Product": ["Laptop", "Phone"]
    })

    context = build_dataset_context(df)
    formatted = format_dataset_context(context)

    assert "Product" in formatted
    assert "Nombre de lignes" in formatted
