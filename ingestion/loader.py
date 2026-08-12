from pathlib import Path


def load_files(repo_path: str):
    files = []

    for path in Path(repo_path).rglob("*"):
        if path.is_file():
            files.append(path)

    return files


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")