import os
import json
from langchain_openai import ChatOpenAI
from openai import OpenAI
from config import OPENAI_CONFIG

def get_openai_llm():
    """Get OpenAI LLM instance for LangChain"""
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", OPENAI_CONFIG['default_model']),
        temperature=OPENAI_CONFIG['temperature'],
        max_tokens=OPENAI_CONFIG['max_tokens']
    )

def get_openai_llm_streaming():
    """Streaming version for direct work with OpenAI API"""
    return OpenAIStreaming()

class OpenAIStreaming:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", OPENAI_CONFIG['default_model'])
    
    def stream(self, messages):
        """Generates streaming response"""
        
        if not self.client.api_key:
            yield "Error: OPENAI_API_KEY not set"
            return
        
        # Convert message format if needed
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                formatted_messages.append(msg)
            else:
                formatted_messages.append({"role": "user", "content": str(msg)})

        try:
            print(f"📄 Making streaming request to OpenAI API")
            
            # Create streaming chat completion
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                stream=True,
                temperature=OPENAI_CONFIG['temperature'],
                max_tokens=OPENAI_CONFIG['max_tokens']
            )
            
            print("✅ Streaming response received")
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"OpenAI API error: {str(e)}"