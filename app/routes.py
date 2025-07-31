from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from .github_utils import download_repo
from .chat_utils import ask_ai
from .rag_utils import index_documents, get_answer_from_repo

router = APIRouter()




@router.post("/load_repo")
async def load_repo(req: Request):
    global repo_path_global
    data = await req.json()

    # Завантаження репозиторію
    repo_path = download_repo(data["url"])
    repo_path_global = repo_path

    # Побудова векторної бази (індексація)
    try:
        index_documents(repo_path)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Indexing failed: {e}"})

    return {"message": "Repository downloaded and indexed."}


@router.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message") or data.get("question")
        if not message:
            return JSONResponse(status_code=400, content={"error": "Missing 'message' field"})

        answer = get_answer_from_repo(message)

        return {"answer": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

