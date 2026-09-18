from fastapi import FastAPI

from backend.api.routes.chat import router as chat_router
from backend.api.routes.repositories import router as repositories_router


app = FastAPI(
    title="RepoRAG API",
    description="AI software engineering assistant",
    version="0.1.0",
)

app.include_router(repositories_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }