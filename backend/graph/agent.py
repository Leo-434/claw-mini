import os
from typing import AsyncGenerator
from dotenv import load_dotenv

# Load `.env` from the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Strict adherence to PRD requirement for the latest graph-based API
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

from backend.tools import (
    terminal_tool,
    python_repl_tool,
    fetch_url_tool,
    read_file_tool,
    write_file_tool,
    add_memory_tool,
    search_knowledge_base_tool
)
from backend.memory.prompt_manager import build_system_prompt
from backend.skills.skills_manager import SkillsManager
from backend.memory.session_manager import SessionManager

def get_llm():
    """Initializes the LLM based on environment variables."""
    model_type = os.getenv("MODEL_TYPE", "openai").lower()
    default_model = os.getenv("DEFAULT_MODEL", "gpt-5")
    
    if model_type == "ollama":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            temperature=0.2,
        )
    elif model_type == "deepseek":
        return ChatOpenAI(
            model="deepseek-3.1",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
            temperature=0.2,
            streaming=True
        )
    elif model_type == "dashscope":
        return ChatOpenAI(
            model="qwen3-max",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0.2,
            streaming=True
        )
    elif model_type == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=1.0
        )
    else:
        # Default fallback to OpenAI or compatible (like OpenRouter)
        return ChatOpenAI(
            model="gpt-5.1",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            temperature=0.2,
            streaming=True
        )

def get_mini_openclaw_agent(query: str = ""):
    """Builds and returns the agent executable graph."""
    
    llm = get_llm()
    
    # Bind Core Tools
    tools = [
        terminal_tool,
        python_repl_tool,
        fetch_url_tool,
        read_file_tool,
        write_file_tool,
        search_knowledge_base_tool
    ]
    
    # Dynamic prompt building
    system_prompt_str = build_system_prompt(query)
        
    # Standard LangChain create_agent interface creates a CompiledGraph
    agent_graph = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt_str
    )
    
    return agent_graph

async def stream_chat_response(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """Streams the agent thought process and final response via langgraph streaming."""
    agent_graph = get_mini_openclaw_agent(query=message)
    session_manager = SessionManager(session_id)
    
    # Load past history 
    # LangGraph create_react_agent expects messages context
    history = session_manager.load_history()
    
    # Add new user message
    # For LangGraph state, we pass the messages list
    # Because LangGraph appends automatically to its state
    inputs = {"messages": history + [("user", message)]}
    
    new_messages = []
    
    try:
        final_state = None
        # Stream events to capture Thoughts (Tool calls) and final AI response
        async for event in agent_graph.astream_events(inputs, version="v2"):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    # AI answering stream
                    yield f"data: {chunk.content}\n\n"
                    
            elif kind == "on_tool_start":
                tool_name = event["name"]
                # Stream out what tool is being used
                yield f"data: [THOUGHT] Calling tool: {tool_name}...\n\n"
                
            elif kind == "on_tool_end":
                tool_name = event["name"]
                yield f"data: [THOUGHT] Finished tool: {tool_name}\n\n"
                
            elif kind == "on_chain_end" and not event.get("parent_ids"):
                final_state = event["data"].get("output")
                
        if final_state and "messages" in final_state:
            session_manager.save_history(final_state["messages"])
        
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
