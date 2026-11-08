
import chromadb
from pathlib import Path
import uuid


DB_PATH = Path("data/chroma_db")
COLLECTION_NAME = "autobi_knowledge"


def get_collection():
    """
    Crée ou récupère la collection persistante ChromaDB.
    """
    DB_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(DB_PATH)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "AutoBI-RAG knowledge base"}
    )

    return collection


def add_chunks(chunks, embeddings, metadatas):
    """
    Enregistre les chunks, leurs embeddings et leurs métadonnées.
    """

    if not chunks:
        return

    if len(chunks) != len(embeddings) or len(chunks) != len(metadatas):
        raise ValueError("Les chunks, embeddings et métadonnées doivent avoir la même taille.")

    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    return ids


def search_chunks(query_embedding, top_k=3):
    """
    Recherche les chunks les plus proches d'une question.
    """

    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(top_k, collection.count())
    )

    return results
