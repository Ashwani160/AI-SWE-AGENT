from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "AI Software Engineering Assistant"}


@app.get("/health")
def health():
    return {"status": "ok"}