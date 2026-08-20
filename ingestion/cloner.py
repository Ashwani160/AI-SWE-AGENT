from pathlib import Path

from git import Repo


def clone_repository(repo_url: str, destination: str):
    destination_path = Path(destination)

    if destination_path.exists():
        if (destination_path / ".git").exists():
            return Repo(destination_path)

        raise FileExistsError(
            f"Destination exists but is not a Git repository: {destination}"
        )

    return Repo.clone_from(repo_url, destination)