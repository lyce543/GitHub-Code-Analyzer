import os
import json
from langchain_openai import ChatOpenAI
from openai import OpenAI

def get_openai_llm():
    """Get OpenAI LLM instance for LangChain"""
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.3,
        max_tokens=1024
    )

def get_openai_llm_streaming():
    """Streaming version for direct work with OpenAI API"""
    return OpenAIStreaming()

class OpenAIStreaming:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
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
            print(f"🔄 Making streaming request to OpenAI API")
            
            # Create streaming chat completion
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                stream=True,
                temperature=0.3,
                max_tokens=1024
            )
            
            print("✅ Streaming response received")
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"OpenAI API error: {str(e)}"