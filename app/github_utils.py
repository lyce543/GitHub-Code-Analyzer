import os
import shutil
import subprocess

def download_repo(repo_url: str) -> str:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = f"./repos/{repo_name}"

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    subprocess.run(["git", "clone", repo_url, repo_path], check=True)
    return repo_path
