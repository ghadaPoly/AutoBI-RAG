
from pathlib import Path


def load_documents(corpus_dir="rag/corpus"):
    """
    Charge tous les documents Markdown du corpus RAG.

    Retourne une liste de documents contenant :
    - le contenu du document ;
    - le nom du fichier ;
    - la catégorie du document.
    """

    corpus_path = Path(corpus_dir)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Le dossier du corpus est introuvable : {corpus_path}"
        )

    documents = []

    for file_path in corpus_path.rglob("*.md"):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        documents.append({
            "content": content,
            "source": file_path.name,
            "category": file_path.parent.name,
            "path": str(file_path)
        })

    return documents
