import os
from openai import OpenAI
from config import OPENAI_CONFIG

def ask_ai(prompt: str, repo_path: str) -> str:
    """
    Sends a request to OpenAI with repository context
    """
    # Collect all .py files from the repository
    context = ""
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        context += f"\n\n# File: {file}\n{content}"
                except Exception as e:
                    print(f"⛔ Error reading {file}: {e}")
                    continue

    # Limit context length
    if len(context) > OPENAI_CONFIG['max_context_chars']:
        context = context[-OPENAI_CONFIG['max_context_chars']:]

    # Build final prompt
    full_prompt = f"""You are a senior developer. Below is a GitHub repository content:
{context}

Now answer the question: {prompt}
"""

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", OPENAI_CONFIG['default_model']),
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            temperature=OPENAI_CONFIG['temperature'],
            max_tokens=OPENAI_CONFIG['max_tokens']
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"OpenAI API error: {str(e)}"