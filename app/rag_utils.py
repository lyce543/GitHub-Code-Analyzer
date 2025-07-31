from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from app.llm import get_openrouter_llm
import os

db = None

def load_documents(repo_path):
    from pathlib import Path
    documents = []
    for file in Path(repo_path).rglob("*.py"):
        with open(file, encoding='utf-8') as f:
            documents.append({"text": f.read(), "path": str(file)})
    return documents

def index_documents(repo_path):
    global db
    docs = load_documents(repo_path)
    texts = [doc["text"] for doc in docs]
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.create_documents(texts)
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    db = FAISS.from_documents(splits, embedding)

    # 🔒 Зберігаємо векторну базу у папку "vectorstore"
    db.save_local("vectorstore")

def get_answer_from_repo(question):
    global db
    if db is None:
        print("🟡 FAISS DB not loaded — trying to load from disk...")
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        if not os.path.exists("vectorstore"):
            return "Repository not loaded."
        db = FAISS.load_local("vectorstore", embeddings=embedding, allow_dangerous_deserialization=True)

    print("🟢 RAG answering question:", question)
    llm = get_openrouter_llm()
    qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=db.as_retriever(),
    chain_type_kwargs={"verbose": True}  # ← додано
    )
    return qa.run(question)



