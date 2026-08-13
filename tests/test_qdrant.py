from ingestion.loader import load_files
from ingestion.file_filter import filter_files
from ingestion.documents import create_documents
from ingestion.chunker import split_documents

from rag.embeddings import embeddings
from rag.vector_store import create_collection, add_documents


repo_path = "repositories/requests"

files = load_files(repo_path)
files = filter_files(files)

documents = create_documents(
    files,
    repository="requests",
    repo_path=repo_path,
)
chunks = split_documents(documents)

vector_size = len(
    embeddings.embed_query("test")
)

create_collection(vector_size)

add_documents(chunks, embeddings)

print(f"Inserted {len(chunks)} chunks into Qdrant")