import os
from langchain_openai import ChatOpenAI
from openai import OpenAI
from config import OPENAI_CONFIG, OPENROUTER_CONFIG


def _use_openrouter() -> bool:
    return os.getenv("USE_OPENROUTER", "false").lower() == "true" and bool(os.getenv("OPENROUTER_API_KEY"))


def get_openai_llm():
    if _use_openrouter():
        return ChatOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=OPENROUTER_CONFIG['base_url'],
            model=os.getenv("OPENROUTER_MODEL", OPENROUTER_CONFIG['default_model']),
            temperature=OPENAI_CONFIG['temperature'],
            max_tokens=OPENAI_CONFIG['max_tokens'],
        )
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
        if _use_openrouter():
            self.client = OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url=OPENROUTER_CONFIG['base_url'],
            )
            self.model = os.getenv("OPENROUTER_MODEL", OPENROUTER_CONFIG['default_model'])
        else:
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
