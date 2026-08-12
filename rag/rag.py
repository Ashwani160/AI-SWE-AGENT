from langchain_core.prompts import ChatPromptTemplate

from rag.embeddings import embeddings
from rag.vector_store import search_documents
from rag.generator import llm


prompt = ChatPromptTemplate.from_template(
    """You are an AI software engineering assistant.

Answer the user's question based on the provided repository code.

Explain what the code is doing and mention relevant files or functions when possible.
Do not invent information that is not supported by the provided context.

Repository context:

{context}

User question:

{question}

Answer:
"""
)


def answer_question(question: str):
    results = search_documents(
        question,
        embeddings,
        limit=5,
    )

    context = "\n\n".join(
        result.payload["text"]
        for result in results
    )

    print("\n===== RETRIEVED CONTEXT =====")
    print(context)
    print("=============================\n")

    messages = prompt.format_messages(
        context=context,
        question=question,
    )

    response = llm.invoke(messages)

    return response.content