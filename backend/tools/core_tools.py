import os
import re
import requests
from bs4 import BeautifulSoup
import html2text

from langchain_core.tools import tool
from langchain_community.tools import ShellTool, ReadFileTool, WriteFileTool
from langchain_experimental.tools.python.tool import PythonREPLTool

# ----------------------------------------------------------------------------
# 1. Terminal Tool (Sandboxed ShellTool)
# ----------------------------------------------------------------------------
# For a production system this should be more robust, e.g., using Docker.
# Here we implement basic path restriction and a blacklist.
DANGEROUS_COMMANDS = [
    r"\brm\b.*\b-r\b", r"\bmv\b.*\b/\b", r"\bsudo\b", r"\bchown\b", r"\bchmod\b\s+777",
    r"\bhalt\b", r"\breboot\b", r"\bpoweroff\b", r"\binit\b"
]

from typing import Union, List

class SandboxedShellTool(ShellTool):
    def _run(self, commands: Union[str, List[str]], **kwargs) -> str:
        # Check against blacklist
        commands_str = commands if isinstance(commands, str) else " ".join(commands)
        for pattern in DANGEROUS_COMMANDS:
            if re.search(pattern, commands_str):
                 return f"Security Exception: Command '{commands_str}' matches dangerous pattern and was blocked."
        return super()._run(commands, **kwargs)

# Allow changing directory but keep it relative out of caution
terminal_tool = SandboxedShellTool(name="terminal")

# ----------------------------------------------------------------------------
# 2. Python REPL Tool
# ----------------------------------------------------------------------------
python_repl_tool = PythonREPLTool(name="python_repl")

# ----------------------------------------------------------------------------
# 3. Fetch URL Tool
# ----------------------------------------------------------------------------
@tool("fetch_url")
def fetch_url_tool(url: str) -> str:
    """Fetches a URL and returns its textual representation (cleaned Markdown) to save tokens."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Convert to Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        markdown_text = h.handle(str(soup))
        
        # Truncate if too long (e.g., arbitrarily at 15000 chars to avoid prompt bloat)
        max_chars = 15000
        if len(markdown_text) > max_chars:
            markdown_text = markdown_text[:max_chars] + "\n...[truncated]"
            
        return markdown_text
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

# ----------------------------------------------------------------------------
# 4. Read File Tool
# ----------------------------------------------------------------------------
# Restrict file reading to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

read_file_tool = ReadFileTool(name="read_file", root_dir=PROJECT_ROOT)
write_file_tool = WriteFileTool(name="write_file", root_dir=PROJECT_ROOT)

# ----------------------------------------------------------------------------
# 5. Add Memory Tool
# ----------------------------------------------------------------------------
import datetime

@tool("add_memory")
def add_memory_tool(memory_content: str) -> str:
    """Safely appends a new piece of information or fact into the long-term MEMORY.md file with a timestamp."""
    memory_path = os.path.join(PROJECT_ROOT, "backend", "memory", "MEMORY.md")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Check if the placeholder exists to maintain structure
        content_exists = False
        if os.path.exists(memory_path):
            with open(memory_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    content_exists = True
                    
        with open(memory_path, 'a', encoding='utf-8') as f:
            if not content_exists:
                f.write("# 长期记忆 (MEMORY)\n\n这里记录着与你相关的核心设定、重要决策、偏好设定以及其他跨越单次会话的历史信息。这些信息作为上下文的一部分将在每次对话被载入。\n\n---\n")
            f.write(f"\n- **[{timestamp}]** {memory_content}\n")
            
        return f"Successfully added memory: '{memory_content}' to long-term storage."
    except Exception as e:
        return f"Error adding memory: {str(e)}"

# ----------------------------------------------------------------------------
# 6. Search Knowledge Base Tool (Hybrid LlamaIndex)
# ----------------------------------------------------------------------------
@tool("search_knowledge_base")
def search_knowledge_base_tool(query: str) -> str:
    """Useful for answering questions by querying the local document knowledge base using hybrid search (BM25 + Vector)."""
    # Placeholder implementation, as LlamaIndex hybrid search setup is complex (requires embedding model, setup of vector store etc.)
    # Depending on requirements, we can load a pre-built index here.
    # For now, we will return a mock response or outline the mechanism.
    
    try:
        from llama_index.core import StorageContext, load_index_from_storage
        storage_path = os.path.join(PROJECT_ROOT, "backend", "storage")
        if not os.path.exists(storage_path):
            return "Knowledge base index not found. Please build the index first."
            
        storage_context = StorageContext.from_defaults(persist_dir=storage_path)
        index = load_index_from_storage(storage_context)
        
        # NOTE: Proper hybrid search in LlamaIndex involves combining multiple retrievers 
        # (e.g. BM25Retriever + VectorIndexRetriever). 
        # For simplicity, we fallback to standard vector query if full hybrid is not rigged up.
        query_engine = index.as_query_engine(similarity_top_k=3)
        response = query_engine.query(query)
        return str(response)
        
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"

