from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
import os
import json
from pathlib import Path
import tempfile
import shutil

from .github_utils import download_repo
from .chat_utils import ask_ai
from .rag_utils import index_documents, get_answer_from_repo, get_answer_from_repo_streaming

router = APIRouter()

# Використовуємо файл для збереження стану між запитами
STATE_FILE = "repo_state.json"

def save_repo_state(repo_path: str, repo_url: str):
    """Зберігає стан репозиторію у файл"""
    state = {
        "repo_path": repo_path,
        "repo_url": repo_url,
        "exists": os.path.exists(repo_path)
    }
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f)
    print(f"✅ State saved: {state}")

def load_repo_state():
    """Завантажує стан репозиторію з файлу"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                # Перевіряємо чи існує папка
                if state.get("repo_path") and os.path.exists(state["repo_path"]):
                    print(f"✅ State loaded: {state}")
                    return state["repo_path"]
                else:
                    print(f"❌ Saved path doesn't exist: {state.get('repo_path')}")
        print("❌ No valid state found")
        return None
    except Exception as e:
        print(f"❌ Error loading state: {e}")
        return None

def clear_repo_state():
    """Очищає збережений стан"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print("🗑️ State cleared")

@router.post("/load_repo")
async def load_repo(req: Request):
    try:
        data = await req.json()
        repo_url = data.get("url")
        
        if not repo_url:
            return JSONResponse(status_code=400, content={"error": "Missing repository URL"})

        print(f"🔄 Loading repository: {repo_url}")
        
        # Очищуємо попередній стан
        clear_repo_state()
        
        # Завантаження репозиторію
        repo_path = download_repo(repo_url)
        
        print(f"✅ Repository downloaded to: {repo_path}")

        # Зберігаємо стан
        save_repo_state(repo_path, repo_url)

        # Побудова векторної бази (індексація)
        print("🔄 Starting indexing...")
        index_documents(repo_path)
        print("✅ Indexing completed")

        return {"message": "Repository downloaded and indexed.", "path": repo_path}
        
    except Exception as e:
        print(f"❌ Error in load_repo: {str(e)}")
        clear_repo_state()
        return JSONResponse(status_code=500, content={"error": f"Loading failed: {str(e)}"})

@router.get("/get_repo_structure")
async def get_repo_structure():
    # Завантажуємо стан з файлу
    repo_path_global = load_repo_state()
    
    print(f"🔍 Checking repo_path_global: {repo_path_global}")
    
    if not repo_path_global:
        print("❌ repo_path_global is None")
        return JSONResponse(status_code=400, content={"error": "No repository loaded - repo_path_global is None"})
    
    if not os.path.exists(repo_path_global):
        print(f"❌ Path does not exist: {repo_path_global}")
        clear_repo_state()  # Очищаємо неіснуючий стан
        return JSONResponse(status_code=400, content={"error": f"Repository path does not exist: {repo_path_global}"})
    
    try:
        files = []
        repo_path = Path(repo_path_global)
        print(f"🔍 Scanning repository at: {repo_path}")
        
        # Збираємо всі файли з їхнім вмістом
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # Відносний шлях від кореня репозиторію
                    relative_path = str(file_path.relative_to(repo_path))
                    
                    # Пропускаємо файли .git та інші системні
                    if '.git' in relative_path or '__pycache__' in relative_path:
                        continue
                    
                    # Читаємо тільки текстові файли
                    if file_path.suffix.lower() in ['.py', '.js', '.html', '.css', '.md', '.txt', '.json', '.yml', '.yaml', '.xml', '.cfg', '.ini', '.env', '.gitignore', '.dockerfile', '']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # Обмежуємо розмір файлу для відображення
                                if len(content) > 50000:  # 50KB limit
                                    content = content[:50000] + "\n\n... (файл обрізано, занадто великий для відображення)"
                        except Exception as read_error:
                            content = f"Error reading file: {str(read_error)}"
                    else:
                        content = f"Binary file ({file_path.suffix})"
                    
                    files.append({
                        "path": relative_path,
                        "content": content,
                        "size": len(content) if isinstance(content, str) else 0
                    })
                    
                except Exception as e:
                    print(f"❌ Error processing file {file_path}: {str(e)}")
                    continue
        
        print(f"✅ Found {len(files)} files")
        return {"files": files}
        
    except Exception as e:
        print(f"❌ Exception in get_repo_structure: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Failed to get repository structure: {str(e)}"})

@router.post("/chat")
async def chat_streaming(request: Request):
    try:
        data = await request.json()
        message = data.get("message") or data.get("question")
        if not message:
            return JSONResponse(status_code=400, content={"error": "Missing 'message' field"})

        # Перевіряємо чи репозиторій завантажений
        repo_path = load_repo_state()
        if not repo_path:
            return JSONResponse(status_code=400, content={"error": "No repository loaded. Please load a repository first."})

        # Використовуємо стрімінгову функцію
        def generate_response():
            try:
                for chunk in get_answer_from_repo_streaming(message):
                    # Відправляємо кожен шматок як Server-Sent Event
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                # Сигналізуємо про завершення
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Залишаємо старий ендпойнт для сумісності
@router.post("/chat_simple")
async def chat_simple(request: Request):
    try:
        data = await request.json()
        message = data.get("message") or data.get("question")
        if not message:
            return JSONResponse(status_code=400, content={"error": "Missing 'message' field"})

        # Перевіряємо чи репозиторій завантажений
        repo_path = load_repo_state()
        if not repo_path:
            return JSONResponse(status_code=400, content={"error": "No repository loaded. Please load a repository first."})

        answer = get_answer_from_repo(message)
        return {"answer": answer}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Ендпойнт для дебагу
@router.get("/debug/status")
async def debug_status():
    repo_path_global = load_repo_state()
    return {
        "repo_path_global": repo_path_global,
        "path_exists": os.path.exists(repo_path_global) if repo_path_global else False,
        "current_working_directory": os.getcwd(),
        "state_file_exists": os.path.exists(STATE_FILE)
    }

# Додатковий ендпойнт для очищення стану
@router.post("/clear_repo")
async def clear_repo():
    """Очищає завантажений репозиторій та стан"""
    try:
        repo_path = load_repo_state()
        
        # Видаляємо папку репозиторію якщо існує
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            print(f"🗑️ Removed repository folder: {repo_path}")
        
        # Видаляємо векторну базу
        if os.path.exists("vectorstore"):
            shutil.rmtree("vectorstore")
            print("🗑️ Removed vector store")
        
        # Очищаємо стан
        clear_repo_state()
        
        return {"message": "Repository cleared successfully"}
        
    except Exception as e:
        print(f"❌ Error clearing repository: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Failed to clear repository: {str(e)}"})