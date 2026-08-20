from rag.embeddings import embeddings
from rag.vector_store import search_documents
from rag.generator import llm
from langchain_core.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_template(
    """You are an AI software engineering assistant.

Answer the user's question using the provided repository context.

Explain the relevant code clearly.
Mention file paths when useful.
Do not invent information that is not supported by the context.

Repository context:

{context}

Question:

{question}
"""
)


def answer_question(
    question: str,
    repository: str,
    collection_name: str,
):
    results = search_documents(
        query=question,
        embeddings=embeddings,
        limit=5,
        repository=repository,
        collection_name=collection_name,
    )

    context = "\n\n".join(
        result.payload["text"]
        for result in results
    )

    messages = prompt.format_messages(
        context=context,
        question=question,
    )

    response = llm.invoke(messages)

    sources = [
        result.payload["file_path"]
        for result in results
    ]

    return response.content, sources