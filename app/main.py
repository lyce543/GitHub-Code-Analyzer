from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from dotenv import load_dotenv
import os

# Завантажуємо змінні середовища
load_dotenv()

# Перевіряємо наявність необхідних змінних
required_env_vars = ["OPENROUTER_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file")
else:
    print("✅ Environment variables loaded successfully")

app = FastAPI(title="GitHub AI Code Analyzer", version="1.0.0")

# Додаємо CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключаємо роути
app.include_router(router)

# Статичні файли (фронтенд)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GitHub AI Code Analyzer...")
    print("📝 Make sure you have set OPENROUTER_API_KEY in your .env file")
    uvicorn.run(app, host="0.0.0.0", port=8000)