from ingestion.cloner import clone_repository


repo_url = "https://github.com/psf/requests.git"
destination = "repositories/requests"

clone_repository(repo_url, destination)

print("Repository cloned successfully!")

# https://github.com/psf/requests.git