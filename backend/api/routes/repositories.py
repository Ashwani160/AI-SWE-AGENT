from enum import Enum
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.indexing import index_repository
from ingestion.cloner import clone_repository
from rag.vector_store import collection_exists


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


class ChunkingStrategy(str, Enum):
    LANGUAGE = "language"
    AST = "ast"


class RepositoryIndexRequest(BaseModel):
    repository_url: str
    repository_name: str
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.LANGUAGE
    reindex: bool = True


@router.post("/index")
def index_repository_endpoint(request: RepositoryIndexRequest):
    destination = Path("repositories") / request.repository_name

    try:
        clone_repository(
            request.repository_url,
            str(destination),
        )
    except FileExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if request.chunking_strategy == ChunkingStrategy.AST:
        collection_name = "code_chunks_ast"
    else:
        collection_name = "code_chunks_lang"

    if not request.reindex:
        if not collection_exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"No {request.chunking_strategy.value} index exists. "
                    "Set reindex to true to create it."
                ),
            )

        return {
            "message": "Repository ready. Using existing index.",
            "repository": request.repository_name,
            "chunking_strategy": request.chunking_strategy.value,
            "indexed": False,
            "collection": collection_name,
        }

    try:
        result = index_repository(
            repo_path=str(destination),
            repository=request.repository_name,
            collection_name=collection_name,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Repository indexing failed.",
        ) from error

    return {
        "message": "Repository indexed successfully",
        "repository": request.repository_name,
        "chunking_strategy": request.chunking_strategy.value,
        "indexed": True,
        **result,
    }
