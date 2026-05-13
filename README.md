# CODEX AI — GitHub Code Intelligence

> Paste a GitHub URL. Ask anything. Understand any codebase in minutes.

CODEX AI is a self-hosted web application that clones any public GitHub repository, indexes its source code using vector embeddings, and lets you ask questions about it in plain English — powered by RAG (Retrieval-Augmented Generation) and GPT-4o.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-blue?style=flat-square)

---

## Features

- **AI Q&A on any repository** — ask about functions, architecture, patterns, or logic in plain English
- **Semantic code search** — FAISS vector store retrieves the most relevant code chunks for each question
- **Real-time streaming** — answers stream token-by-token via Server-Sent Events
- **IDE-like file explorer** — browse the full file tree and view source code with line numbers
- **Beautiful landing page** — polished dark UI with animated hero, feature accordion, and product mockup
- **One-click repo management** — load and clear repositories without restarting the server

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn |
| AI / LLM | OpenAI GPT-4o |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | FAISS (local) |
| RAG Pipeline | LangChain |
| Repo Cloning | Git (subprocess) |
| Frontend | Vanilla HTML / CSS / JS (SPA) |

---

## Project Structure

```
GitHub-Code-Analyzer/
├── app/
│   ├── main.py          # FastAPI app, middleware, static file serving
│   └── routes.py        # API endpoints (load_repo, chat, get_repo_structure, clear_repo)
├── utils/
│   ├── rag_utils.py     # RAG pipeline: indexing, retrieval, answer generation
│   ├── llm.py           # OpenAI LLM wrapper with streaming support
│   ├── github_utils.py  # Repository cloning via git
│   └── chat_utils.py    # Basic chat without RAG (legacy)
├── frontend/
│   ├── index.html       # Landing page
│   └── app.html         # Main application (file explorer + code viewer + chat)
├── config.py            # All configuration constants
├── run.py               # Development server entry point
├── requirements.txt
└── .env                 # API keys (not committed)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- `git` available in PATH
- OpenAI API key with available balance

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/GitHub-Code-Analyzer.git
cd GitHub-Code-Analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
```

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key | required |
| `OPENAI_MODEL` | Model used for chat responses | `gpt-4o` |

### Run

```bash
python run.py
```

Open your browser at **http://localhost:8000**

---

## How It Works

```
User pastes GitHub URL
        ↓
  git clone → repos/
        ↓
  Read all .py files
        ↓
  Split into 1000-char chunks (200 overlap)
        ↓
  OpenAI Embeddings → FAISS vector store
        ↓
  User asks a question
        ↓
  Semantic search → top 4 relevant chunks
        ↓
  GPT-4o generates answer (streaming)
        ↓
  Answer streams to browser via SSE
```

### RAG Parameters

| Parameter | Value |
|---|---|
| Chunk size | 1000 characters |
| Chunk overlap | 200 characters |
| Retrieved chunks (k) | 4 |
| Embedding model | `text-embedding-3-small` |
| LLM temperature | 0.3 |
| Max tokens | 1024 |

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/load_repo` | Clone and index a GitHub repository |
| `GET` | `/get_repo_structure` | Get all files with content for the file explorer |
| `POST` | `/chat` | Stream an AI answer (Server-Sent Events) |
| `POST` | `/chat_simple` | Non-streaming version of chat |
| `POST` | `/clear_repo` | Delete the loaded repo and vector store |
| `GET` | `/debug/status` | Check internal server state |

### Example: Load a repository

```bash
curl -X POST http://localhost:8000/load_repo \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/owner/repository"}'
```

### Example: Ask a question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How does the authentication system work?"}'
```

Response streams as Server-Sent Events:
```
data: {"chunk": "The authentication"}
data: {"chunk": " system uses..."}
data: {"done": true}
```

---

## Frontend

The app has two pages:

- **`/`** — Landing page with hero, features accordion, how-it-works, and CTA
- **`/app.html`** — The main tool: file explorer · code viewer · AI chat panel

Both share the same CODEX design system: dark theme, amber accents, Syne + Outfit + Fira Code typography.

---

## Limitations

- Only **Python files** (`.py`) are indexed for semantic search; other file types are displayed in the viewer but not embedded
- Only **public** GitHub repositories can be cloned (no authentication)
- Repositories are stored locally in `repos/` — large repos may take longer to index
- The vector store is single-tenant: loading a new repo replaces the previous one

---

## License

MIT
