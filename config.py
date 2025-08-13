# Configuration file for GitHub AI Code Analyzer

# OpenAI API Configuration
OPENAI_CONFIG = {
    'default_model': 'gpt-4o',
    'embedding_model': 'text-embedding-3-small',
    'temperature': 0.3,
    'max_tokens': 1024,
    'max_context_chars': 8000,
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'retrieval_k': 4,  # Number of documents to retrieve for RAG
}

# Application Configuration
APP_CONFIG = {
    'app_title': 'GitHub AI Code Analyzer',
    'app_version': '1.0.0',
    'host': '0.0.0.0',
    'port': 8000,
    'repos_folder': 'repos',
    'vectorstore_path': 'vectorstore',
    'state_file': 'repo_state.json',
    'frontend_folder': 'frontend',
}

# File processing configuration
FILE_PROCESSING_CONFIG = {
    'supported_extensions': ['.py', '.js', '.html', '.css', '.md', '.txt', '.json', '.yml', '.yaml', '.xml', '.cfg', '.ini', '.env', '.gitignore', '.dockerfile'],
    'max_file_size_display': 50000,  # 50KB limit for file display
    'excluded_folders': ['.git', '__pycache__', 'node_modules', '.vscode', '.idea'],
}

# CORS Configuration
CORS_CONFIG = {
    'allow_origins': ["*"],
    'allow_credentials': True,
    'allow_methods': ["*"],
    'allow_headers': ["*"],
}