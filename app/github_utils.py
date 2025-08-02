import os
import shutil
import subprocess

def download_repo(repo_url: str) -> str:
    """
    Завантажує репозиторій з GitHub та повертає шлях до нього
    """
    try:
        # Отримуємо назву репозиторію з URL
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
            
        repo_path = f"./repos/{repo_name}"
        
        print(f"🔄 Downloading to: {repo_path}")

        # Створюємо папку repos якщо її немає
        os.makedirs("./repos", exist_ok=True)

        # Видаляємо існуючу папку якщо є
        if os.path.exists(repo_path):
            print(f"🗑️ Removing existing directory: {repo_path}")
            shutil.rmtree(repo_path)

        # Клонуємо репозиторій
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