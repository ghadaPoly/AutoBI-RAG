
import pandas as pd

from agent.agent import plan_question


if __name__ == "__main__":

    df = pd.DataFrame({
        "Region": ["Paris", "Lyon", "Paris", "Lille"],
        "Revenue": [1200, 800, 1500, 600],
        "Quantity": [2, 1, 3, 1]
    })

    question = (
        "Quel est le chiffre d'affaires total par région ?"
    )

    try:
        result = plan_question(
            df,
            question,
            dataset_name="sales.csv"
        )

        print("\n--- PLAN DE L'AGENT ---")
        print(result)

    except Exception as error:
        print("Erreur :", error)
