from git import Repo


def clone_repository(repo_url: str, destination: str):
    Repo.clone_from(repo_url, destination)