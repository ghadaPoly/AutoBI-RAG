
from agent.dataset_context import (
    build_dataset_context,
    format_dataset_context
)

from agent.prompts import DATASET_CONTEXT_PROMPT
from agent.llm_client import ask_llm


def ask_about_dataset(df, question, dataset_name="dataset"):
    """
    Permet à l'utilisateur de poser une question
    concernant la structure de son dataset.
    """

    if not question or not question.strip():
        raise ValueError("La question est obligatoire.")

    context = build_dataset_context(
        df,
        dataset_name=dataset_name
    )

    formatted_context = format_dataset_context(context)

    prompt = DATASET_CONTEXT_PROMPT.format(
        dataset_context=formatted_context,
        question=question
    )

    return ask_llm(prompt)
