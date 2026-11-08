
from rag.document_loader import load_documents
from rag.chunker import split_text
from rag.embeddings import generate_embeddings
from rag.vector_store import add_chunks, search_chunks


def index_documents():
    """
    Charge, découpe et indexe les documents du corpus dans ChromaDB.
    """

    documents = load_documents()

    all_chunks = []
    all_metadatas = []

    for document in documents:
        chunks = split_text(
            document["content"],
            chunk_size=500,
            overlap=80
        )

        for index, chunk in enumerate(chunks):
            all_chunks.append(chunk)

            all_metadatas.append({
                "source": document["source"],
                "category": document["category"],
                "chunk_index": index
            })

    if not all_chunks:
        return 0

    embeddings = generate_embeddings(all_chunks)

    add_chunks(
        chunks=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas
    )

    return len(all_chunks)


def retrieve_knowledge(question, top_k=3):
    """
    Recherche les passages les plus pertinents pour une question.
    """

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    query_embedding = generate_embeddings([question])[0]

    results = search_chunks(
        query_embedding=query_embedding,
        top_k=top_k
    )

    knowledge = []

    if not results or not results.get("documents"):
        return knowledge

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        knowledge.append({
            "content": document,
            "source": metadata["source"],
            "category": metadata["category"],
            "distance": float(distance)
        })

    return knowledge
