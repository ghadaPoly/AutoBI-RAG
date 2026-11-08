
from agent.llm_client import ask_llm


if __name__ == "__main__":

    question = (
        "Tu es un assistant de Business Intelligence. "
        "Explique en deux phrases ce qu'est un KPI."
    )

    try:
        response = ask_llm(question)

        print("\n--- Réponse du LLM ---\n")
        print(response)

    except Exception as error:
        print("Erreur de connexion :", error)
