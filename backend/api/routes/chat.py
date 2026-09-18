from enum import Enum

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.chat import answer_question
from rag.vector_store import collection_exists


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChunkingStrategy(str, Enum):
    LANGUAGE = "language"
    AST = "ast"


class ChatRequest(BaseModel):
    question: str
    repository_name: str
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.LANGUAGE


@router.post("")
def chat(request: ChatRequest):
    collection_name = (
        "code_chunks_ast"
        if request.chunking_strategy == ChunkingStrategy.AST
        else "code_chunks_lang"
    )

    if not collection_exists(collection_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No {request.chunking_strategy.value} index exists. "
                "Index the repository before asking questions."
            ),
        )

    try:
        answer, sources = answer_question(
            question=request.question,
            repository=request.repository_name,
            collection_name=collection_name,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to answer the question.",
        ) from error

    return {
        "answer": answer,
        "sources": sources,
    }
