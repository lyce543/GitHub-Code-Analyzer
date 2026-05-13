import os
from langchain_openai import ChatOpenAI
from openai import OpenAI
from config import OPENAI_CONFIG


def get_openai_llm():
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", OPENAI_CONFIG['default_model']),
        temperature=OPENAI_CONFIG['temperature'],
        max_tokens=OPENAI_CONFIG['max_tokens'],
    )


def get_openai_llm_streaming():
    return OpenAIStreaming()


class OpenAIStreaming:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", OPENAI_CONFIG['default_model'])

    def stream(self, messages):
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                formatted_messages.append(msg)
            else:
                formatted_messages.append({"role": "user", "content": str(msg)})

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                stream=True,
                temperature=OPENAI_CONFIG['temperature'],
                max_tokens=OPENAI_CONFIG['max_tokens'],
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"API error: {str(e)}"
