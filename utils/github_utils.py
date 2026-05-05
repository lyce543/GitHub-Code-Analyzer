import os
import stat
import shutil
import subprocess
from config import APP_CONFIG


def _force_remove(path: str):
    """Remove directory tree, handling Windows read-only files in .git."""
    def _on_error(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=_on_error)

def _normalize_github_url(url: str) -> tuple[str, str]:
    """Strips /tree/*, /blob/*, /commits/* etc. and returns (clone_url, repo_name)."""
    import re
    url = url.strip().rstrip("/")
    # Remove trailing .git
    if url.endswith(".git"):
        url = url[:-4]
    # Extract base repo URL: https://github.com/owner/repo
    match = re.match(r"(https?://github\.com/[^/]+/[^/]+)(/.*)?$", url)
    if match:
        url = match.group(1)
    repo_name = url.split("/")[-1]
    return url, repo_name


def download_repo(repo_url: str) -> str:
    """
    Downloads repository from GitHub and returns path to it
    """
    try:
        clone_url, repo_name = _normalize_github_url(repo_url)

        repo_path = f"./{APP_CONFIG['repos_folder']}/{repo_name}"
        
        print(f"🔄 Downloading to: {repo_path}")

        # Create repos folder if it doesn't exist
        os.makedirs(f"./{APP_CONFIG['repos_folder']}", exist_ok=True)

        # Remove existing folder if exists
        if os.path.exists(repo_path):
            print(f"🗑️ Removing existing directory: {repo_path}")
            _force_remove(repo_path)

        # Clone repository
        print(f"⬇️ Cloning repository from: {clone_url}")
        result = subprocess.run(
            ["git", "clone", clone_url, repo_path],
            check=True, 
            capture_output=True, 
            text=True
        )
        
        print(f"✅ Repository cloned successfully")
        print(f"📁 Repository path: {os.path.abspath(repo_path)}")
        
        return repo_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git clone failed: {e}")
        print(f"Git stdout: {e.stdout}")
        print(f"Git stderr: {e.stderr}")
        raise Exception(f"Failed to clone repository: {e.stderr}")
    except Exception as e:
        print(f"❌ Error in download_repo: {str(e)}")
        raise