import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("LLM_MODEL", "openrouter/free")
BASE_URL = "https://openrouter.ai/api/v1"


def get_client():
    """Crée le client de connexion à OpenRouter (API compatible OpenAI)."""
    if not API_KEY:
        raise ValueError("La clé OPENROUTER_API_KEY est absente du fichier .env")

    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def ask_llm(prompt):
    """Envoie un prompt au LLM et retourne sa réponse textuelle."""
    if not prompt or not prompt.strip():
        raise ValueError("Le prompt ne peut pas être vide.")

    client = get_client()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("Le modèle n'a retourné aucune réponse.")

    return text