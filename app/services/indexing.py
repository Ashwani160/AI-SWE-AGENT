from ingestion.loader import load_files
from ingestion.file_filter import filter_files
from ingestion.documents import create_documents
from ingestion.chunker import split_documents as split_language_documents
from ingestion.chunker_ast import split_documents as split_ast_documents

from rag.embeddings import embeddings
from rag.vector_store import create_collection, add_documents


def index_repository(
    repo_path: str,
    repository: str,
    collection_name: str = "code_chunks_lang",
):
    print("Loading repository files...")

    files = load_files(repo_path)
    files = filter_files(files)

    print(f"Found {len(files)} relevant files.")

    documents = create_documents(
        files,
        repository=repository,
        repo_path=repo_path,
    )

    print("Splitting files into chunks...")

    if collection_name == "code_chunks_ast":
        chunks = split_ast_documents(documents)
    else:
        chunks = split_language_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Creating vector collection...")

    vector_size = len(
        embeddings.embed_query("test")
    )

    create_collection(
        vector_size,
        collection_name=collection_name,
    )

    print("Generating embeddings and storing vectors...")

    add_documents(
        chunks,
        embeddings,
        collection_name=collection_name,
    )

    print("Repository indexed successfully.")

    return {
        "files": len(files),
        "chunks": len(chunks),
        "collection": collection_name,
    }