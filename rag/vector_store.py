from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from uuid import uuid4


client = QdrantClient(path="./qdrant_data")

DEFAULT_COLLECTION = "code_chunks_lang"


def create_collection(
    vector_size: int,
    collection_name: str = DEFAULT_COLLECTION,
):
    collections = client.get_collections().collections

    if collection_name not in [c.name for c in collections]:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )


def add_documents(
    documents,
    embeddings,
    collection_name: str = DEFAULT_COLLECTION,
):
    vectors = embeddings.embed_documents(
        [doc.page_content for doc in documents]
    )

    points = []

    for document, vector in zip(documents, vectors):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "text": document.page_content,
                    **document.metadata,
                },
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
    )
    
def search_documents(
    query: str,
    embeddings,
    limit: int = 5,
    repository: str | None = None,
    score_threshold: float | None = None,
    collection_name: str = DEFAULT_COLLECTION,
):
    query_vector = embeddings.embed_query(query)

    query_filter = None

    if repository:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="repository",
                    match=MatchValue(value=repository),
                )
            ]
        )

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
        score_threshold=score_threshold,
    )

    return results.points