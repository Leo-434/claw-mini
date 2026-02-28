import os
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

SESSIONS_DIR = os.path.join(PROJECT_ROOT, "backend", "sessions")
MEMORY_FILE_PATH = os.path.join(PROJECT_ROOT, "backend", "memory", "MEMORY.md")
FAISS_INDEX_PATH = os.path.join(SESSIONS_DIR, "memory_faiss_index")

def get_embeddings():
    """Initializes embeddings based on environment variables."""
    model_type = os.getenv("MODEL_TYPE", "openai").lower()
    
    if True:
        return OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBED_MODEL", "qwen2.5:14b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        )
    elif model_type in ["deepseek", "dashscope", "openai"]:
        # Fallback to OpenAI compatible embeddings for API providers
        # Usually, they might provide their own embedding models
        # For this example, we'll try to use standard OpenAI setup if specific isn't provided
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv(f"{model_type.upper()}_API_KEY", os.getenv("OPENAI_API_KEY")),
            base_url=os.getenv(f"{model_type.upper()}_BASE_URL", os.getenv("OPENAI_BASE_URL"))
        )
    elif model_type == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    return OllamaEmbeddings(model="nomic-embed-text")

def rebuild_memory_index():
    """Reads MEMORY.md, splits it, and builds a FAISS index."""
    if not os.path.exists(MEMORY_FILE_PATH):
        return None
        
    try:
        loader = TextLoader(MEMORY_FILE_PATH, encoding='utf-8')
        documents = loader.load()
        
        # Split by Markdown headers
        text_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        if not docs:
            # If the file is empty or only has short text, create a dummy doc
            docs = [Document(page_content="[Empty Memory]")]
            
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(docs, embeddings)
        
        # Save locally
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        vectorstore.save_local(FAISS_INDEX_PATH)
        return vectorstore
    except Exception as e:
        print(f"Error rebuilding memory index: {e}")
        return None

def get_relevant_memory(query: str, k: int = 3) -> str:
    """Retrieves relevant memory chunks for the given query."""
    if not query.strip():
        # If no query provided, just return the raw file if it's small, or nothing
        try:
            with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:1000] if len(content) > 1000 else content
        except Exception:
            return ""
            
    embeddings = get_embeddings()
    try:
        # Check if index exists and if it is up-to-date
        index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
        should_rebuild = True
        
        if os.path.exists(index_file):
            if os.path.exists(MEMORY_FILE_PATH):
                memory_mtime = os.path.getmtime(MEMORY_FILE_PATH)
                index_mtime = os.path.getmtime(index_file)
                if index_mtime > memory_mtime:
                    should_rebuild = False  # Index is fresh
            else:
                should_rebuild = False # No memory file, so nothing to rebuild
        
        if not should_rebuild:
            vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            vectorstore = rebuild_memory_index()
            if not vectorstore:
                return ""
                
        # Search
        docs = vectorstore.similarity_search(query, k=k)
        
        if not docs:
            return ""
            
        return "\n\n...\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        # Fallback to naive reading if RAG fails
        print(f"Error retrieving from memory index: {e}")
        try:
            with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:1000]
        except Exception:
            return ""
