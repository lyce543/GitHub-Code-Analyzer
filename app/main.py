from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check for required environment variables
required_env_vars = ["OPENROUTER_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file")
else:
    print("✅ Environment variables loaded successfully")

app = FastAPI(title="GitHub AI Code Analyzer", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

# Static files (frontend)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GitHub AI Code Analyzer...")
    print("📝 Make sure you have set OPENROUTER_API_KEY in your .env file")
    uvicorn.run(app, host="0.0.0.0", port=8000)