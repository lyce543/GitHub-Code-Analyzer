import os
import requests
import json
from langchain_openai import ChatOpenAI

def get_openrouter_llm():
    return ChatOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        model=os.getenv("MODEL_ID", "openai/gpt-4o"),
        temperature=0.3,
        max_tokens=1024
    )

def get_openrouter_llm_streaming():
    """Стрімінгова версія для прямої роботи з OpenRouter API"""
    return OpenRouterStreaming()

class OpenRouterStreaming:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("MODEL_ID", "openai/gpt-4o")
    
    def stream(self, messages):
        """Генерує стрімінгову відповідь"""
        
        if not self.api_key:
            yield "Error: OPENROUTER_API_KEY not set"
            return
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "repo-analyzer",
            "Content-Type": "application/json",
        }

        # Конвертуємо формат повідомлень
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                formatted_messages.append(msg)
            else:
                formatted_messages.append({"role": "user", "content": str(msg)})

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": True,
            "temperature": 0.3,
            "max_tokens": 1024
        }

        try:
            print(f"🔄 Making streaming request to {self.base_url}/chat/completions")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=30
            )
            
            if response.status_code != 200:
                yield f"Error: {response.status_code} - {response.text}"
                return

            print("✅ Streaming response received")
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:].strip()  # Видаляємо 'data: '
                        
                        if data_str == '[DONE]':
                            break
                            
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta and delta['content']:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            yield f"Network error: {str(e)}"
        except Exception as e:
            yield f"Streaming error: {str(e)}"