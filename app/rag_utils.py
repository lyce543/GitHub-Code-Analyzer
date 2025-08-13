from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from app.llm import get_openai_llm, get_openai_llm_streaming
import os
import json

db = None
VECTORSTORE_PATH = "vectorstore"
STATE_FILE = "repo_state.json"

def get_embeddings():
    """Get OpenAI embeddings instance"""
    return OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-3-small"  # or text-embedding-3-large for better quality
    )

def load_repo_state():
    """Loads repository state from file"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                if state.get("repo_path") and os.path.exists(state["repo_path"]):
                    return state["repo_path"]
        return None
    except Exception as e:
        print(f"❌ Error loading state in rag_utils: {e}")
        return None

def load_documents(repo_path):
    from pathlib import Path
    documents = []
    for file in Path(repo_path).rglob("*.py"):
        try:
            with open(file, encoding='utf-8') as f:
                documents.append({"text": f.read(), "path": str(file)})
        except Exception as e:
            print(f"❌ Error reading file {file}: {e}")
            continue
    return documents

def index_documents(repo_path):
    global db
    docs = load_documents(repo_path)
    
    if not docs:
        raise Exception("No Python files found in repository")
    
    texts = [doc["text"] for doc in docs]
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.create_documents(texts)
    
    # Use OpenAI embeddings
    embedding = get_embeddings()
    
    print(f"🔄 Creating embeddings for {len(splits)} chunks using OpenAI...")
    db = FAISS.from_documents(splits, embedding)

    # Save vector database
    if os.path.exists(VECTORSTORE_PATH):
        import shutil
        shutil.rmtree(VECTORSTORE_PATH)
    
    db.save_local(VECTORSTORE_PATH)
    print(f"✅ Indexed {len(docs)} files, created {len(splits)} chunks with OpenAI embeddings")

def ensure_db_loaded():
    """Ensures that vector database is loaded"""
    global db
    
    if db is not None:
        return True
    
    print("🟡 FAISS DB not loaded — trying to load from disk...")
    
    if not os.path.exists(VECTORSTORE_PATH):
        print(f"❌ Vector store path doesn't exist: {VECTORSTORE_PATH}")
        return False
    
    try:
        # Use same embedding model for loading
        embedding = get_embeddings()
        db = FAISS.load_local(VECTORSTORE_PATH, embeddings=embedding, allow_dangerous_deserialization=True)
        print("✅ Vector store loaded successfully with OpenAI embeddings")
        return True
    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return False

def get_answer_from_repo(question):
    global db
    
    # Check if repository is loaded
    repo_path = load_repo_state()
    if not repo_path:
        return "❌ No repository loaded. Please load a repository first."
    
    # Ensure vector database is loaded
    if not ensure_db_loaded():
        return "❌ Failed to load vector database. Please reload the repository."

    print("🟢 RAG answering question:", question)
    try:
        llm = get_openai_llm()
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=db.as_retriever(),
            chain_type_kwargs={"verbose": True}
        )
        return qa.run(question)
    except Exception as e:
        print(f"❌ Error in get_answer_from_repo: {e}")
        return f"Error generating answer: {str(e)}"

def get_answer_from_repo_streaming(question):
    """Streaming version for getting answers"""
    global db
    
    # Check if repository is loaded
    repo_path = load_repo_state()
    if not repo_path:
        yield "❌ No repository loaded. Please load a repository first."
        return
    
    # Ensure vector database is loaded
    if not ensure_db_loaded():
        yield "❌ Failed to load vector database. Please reload the repository."
        return

    print("🟢 RAG answering question with streaming:", question)
    
    try:
        # Get relevant documents using OpenAI embeddings
        retriever = db.as_retriever(search_kwargs={"k": 4})
        docs = retriever.get_relevant_documents(question)
        
        if not docs:
            yield "No relevant documents found in the repository."
            return
        
        # Create context from relevant documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Build prompt
        prompt = f"""Based on the following code repository context, please answer the question.

Context from repository:
{context}

Question: {question}

Please provide a detailed and helpful answer based on the code context above."""

        # Use streaming OpenAI model
        llm = get_openai_llm_streaming()
        
        # Generate response in chunks
        for chunk in llm.stream([{"role": "user", "content": prompt}]):
            yield chunk
            
    except Exception as e:
        print(f"❌ Error in get_answer_from_repo_streaming: {e}")
        yield f"Error generating response: {str(e)}"