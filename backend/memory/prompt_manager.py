import os

def read_and_truncate_file(file_path: str, max_chars: int = 20000) -> str:
    """Reads a markdown file and truncates it if it exceeds max_chars."""
    if not os.path.exists(file_path):
        return ""
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if len(content) > max_chars:
            return content[:max_chars] + "\n...[truncated]\n"
        return content
    except Exception as e:
        return f"Error reading {os.path.basename(file_path)}: {str(e)}\n"

def build_system_prompt(query: str = "") -> str:
    """
    Assembles the core 6 Markdown files into the final System Prompt.
    Order: SKILLS_SNAPSHOT, SOUL, IDENTITY, USER, AGENTS, MEMORY.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Dynamically hot-plug skills before building the prompt
    try:
        from backend.skills.skills_manager import SkillsManager
        SkillsManager.generate_snapshot()
    except Exception as e:
        print(f"Error hot-plugging skills: {e}")
    
    # Paths to the core files
    files = {
        "SKILLS_SNAPSHOT": os.path.join(project_root, "backend", "skills", "SKILLS_SNAPSHOT.md"),
        "SOUL": os.path.join(project_root, "backend", "workspace", "SOUL.md"),
        "IDENTITY": os.path.join(project_root, "backend", "workspace", "IDENTITY.md"),
        "USER": os.path.join(project_root, "backend", "workspace", "USER.md"),
        "AGENTS": os.path.join(project_root, "backend", "workspace", "AGENTS.md"),
    }
    
    prompt_parts = []
    
    for name, path in files.items():
        content = read_and_truncate_file(path)
        if content.strip():
            # Add a clear separator between sections
            prompt_parts.append(f"<!-- BEGIN {name} -->\n{content}\n<!-- END {name} -->")
            
    # Process MEMORY dynamically using RAG
    if query:
        # Import here to avoid circular dependencies
        try:
            from backend.memory.memory_retriever import get_relevant_memory
            memory_content = get_relevant_memory(query)
            if memory_content.strip():
                prompt_parts.append(f"<!-- BEGIN MEMORY -->\n{memory_content}\n<!-- END MEMORY -->")
        except ImportError:
            # Fallback
            memory_path = os.path.join(project_root, "backend", "memory", "MEMORY.md")
            content = read_and_truncate_file(memory_path)
            if content.strip():
                prompt_parts.append(f"<!-- BEGIN MEMORY -->\n{content}\n<!-- END MEMORY -->")
    else:
        # Fallback if no query is provided (e.g. initial start)
        memory_path = os.path.join(project_root, "backend", "memory", "MEMORY.md")
        content = read_and_truncate_file(memory_path)
        if content.strip():
            prompt_parts.append(f"<!-- BEGIN MEMORY -->\n{content}\n<!-- END MEMORY -->")
            
    final_prompt = "\n\n".join(prompt_parts)
    return final_prompt
