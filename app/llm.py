import os
from langchain_openai import ChatOpenAI

def get_openrouter_llm():
    return ChatOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL"),
        model=os.getenv("MODEL_ID"),
        temperature=0.3,
        max_tokens=1024
    )