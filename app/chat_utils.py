import os
import requests

def ask_ai(prompt: str, repo_path: str) -> str:
    """
    Відправляє запит до AI з контекстом репозиторію
    """
    # Збираємо всі .py файли з репозиторію
    context = ""
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        context += f"\n\n# File: {file}\n{content}"
                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")
                    continue

    # Обмежимо довжину контексту
    max_context_chars = 8000
    if len(context) > max_context_chars:
        context = context[-max_context_chars:]

    # Складання фінального промпту
    full_prompt = f"""You are a senior developer. Below is a GitHub repository content:
{context}

Now answer the question: {prompt}
"""

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "repo-analyzer",
        "Content-Type": "application/json",
    }

    payload = {
        "model": os.getenv("MODEL_ID", "openai/gpt-4o"),
        "messages": [
            {"role": "user", "content": full_prompt}
        ]
    }

    try:
        response = requests.post(
            f"{os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')}/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Request error: {str(e)}"