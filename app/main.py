from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from dotenv import load_dotenv
from config import APP_CONFIG, CORS_CONFIG, OPENAI_CONFIG
import os

# Load environment variables
load_dotenv()

# Check for required environment variables
required_env_vars = ["OPENAI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"⛔ Missing environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file")
else:
    print("✅ Environment variables loaded successfully")
    print(f"🤖 Using OpenAI model: {os.getenv('OPENAI_MODEL', OPENAI_CONFIG['default_model'])}")
    print(f"🔗 Using OpenAI embeddings: {OPENAI_CONFIG['embedding_model']}")

app = FastAPI(
    title=APP_CONFIG['app_title'], 
    version=APP_CONFIG['app_version']
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG['allow_origins'],
    allow_credentials=CORS_CONFIG['allow_credentials'],
    allow_methods=CORS_CONFIG['allow_methods'],
    allow_headers=CORS_CONFIG['allow_headers'],
)

# Include routes
app.include_router(router)

# Static files (frontend)
app.mount("/", StaticFiles(directory=APP_CONFIG['frontend_folder'], html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port'],
        reload_excludes=["repos/*", "vectorstore/*", "repo_state.json"],
    )