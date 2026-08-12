from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from uuid import uuid4


client = QdrantClient(path="./qdrant_data")

COLLECTION_NAME = "code_chunks"


def create_collection(vector_size: int):
    collections = client.get_collections().collections

    if COLLECTION_NAME not in [c.name for c in collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )


def add_documents(documents, embeddings):
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
        collection_name=COLLECTION_NAME,
        points=points,
    )
    
def search_documents(query: str, embeddings, limit: int = 5):
    query_vector = embeddings.embed_query(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
    )

    return results.points