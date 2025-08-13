import os
import shutil
import subprocess
from config import APP_CONFIG

def download_repo(repo_url: str) -> str:
    """
    Downloads repository from GitHub and returns path to it
    """
    try:
        # Get repository name from URL
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
            
        repo_path = f"./{APP_CONFIG['repos_folder']}/{repo_name}"
        
        print(f"🔄 Downloading to: {repo_path}")

        # Create repos folder if it doesn't exist
        os.makedirs(f"./{APP_CONFIG['repos_folder']}", exist_ok=True)

        # Remove existing folder if exists
        if os.path.exists(repo_path):
            print(f"🗑️ Removing existing directory: {repo_path}")
            shutil.rmtree(repo_path)

        # Clone repository
        print(f"⬇️ Cloning repository from: {repo_url}")
        result = subprocess.run(
            ["git", "clone", repo_url, repo_path], 
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