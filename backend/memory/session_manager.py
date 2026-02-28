import os
import json
from typing import List, Dict, Any

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage, messages_to_dict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SESSIONS_DIR = os.path.join(PROJECT_ROOT, "backend", "sessions")

class SessionManager:
    def __init__(self, session_id: str = "main_session"):
        self.session_id = session_id
        self.session_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        
    def load_history(self) -> List[BaseMessage]:
        """Loads conversation history from the local JSON file."""
        if not os.path.exists(self.session_path):
            return []
            
        try:
            with open(self.session_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Convert dicts back to LangChain BaseMessage objects
            # Warning: For ToolMessages to align properly, proper dict structures are needed.
            # Using messages_from_dict or manually parsing depending on LangChain version.
            from langchain_core.messages import messages_from_dict
            return messages_from_dict(data)
        except Exception as e:
            print(f"Error loading session {self.session_id}: {e}")
            return []
            
    def _compress_history(self, messages: List[BaseMessage], max_messages: int = 40) -> List[BaseMessage]:
        """Compresses older messages using an LLM to prevent context bloat."""
        if len(messages) <= max_messages:
            return messages
            
        from backend.graph.agent import get_llm
        
        # 1. Separate system messages and past summaries from the rest
        system_msgs = [m for m in messages if isinstance(m, SystemMessage) and "Summary of previous conversation" not in getattr(m, 'content', '')]
        non_system_msgs = [m for m in messages if not isinstance(m, SystemMessage) and "Summary of previous conversation" not in getattr(m, 'content', '')]
        old_summaries = [m for m in messages if isinstance(m, SystemMessage) and "Summary of previous conversation" in getattr(m, 'content', '')]
        
        if len(non_system_msgs) <= max_messages:
            return messages
            
        # 2. Find split point: roughly half, but align with a HumanMessage to avoid breaking tool call pairs
        num_to_compress = len(non_system_msgs) // 2
        split_index = num_to_compress
        while split_index < len(non_system_msgs) and not isinstance(non_system_msgs[split_index], HumanMessage):
            split_index += 1
            
        if split_index >= len(non_system_msgs):
            # Fallback if no HumanMessage found: just take half
            split_index = num_to_compress
            
        msgs_to_compress = non_system_msgs[:split_index]
        msgs_to_keep = non_system_msgs[split_index:]
        
        # 3. Format conversation for the LLM
        conversation_lines = []
        if old_summaries:
            conversation_lines.append(f"PREVIOUS SUMMARY: {old_summaries[-1].content}")
        
        for m in msgs_to_compress:
            if isinstance(m, HumanMessage):
                text = m.content if isinstance(m.content, str) else str(m.content)
                conversation_lines.append(f"Human: {text}")
            elif isinstance(m, AIMessage):
                text = m.content if m.content and isinstance(m.content, str) else "(Tool usage or complex content)"
                conversation_lines.append(f"AI: {text}")
            elif isinstance(m, ToolMessage):
                text = m.content if isinstance(m.content, str) else str(m.content)
                conversation_lines.append(f"Tool Result: {text[:200]}...")
                
        conversation_str = "\n".join(conversation_lines)
        
        try:
            llm = get_llm()
            prompt = (
                "Please summarize the following conversation history concisely. "
                "Preserve all key facts, constraints, user preferences, and important context. "
                "This summary will serve as memory for future interactions.\n\n"
                f"{conversation_str}"
            )
            
            summary_response = llm.invoke(prompt)
            summary_message = SystemMessage(content=f"Summary of previous conversation:\n{summary_response.content}")
            
            # Combine back: original system msgs + new summary + kept msgs
            return system_msgs + [summary_message] + msgs_to_keep
            
        except Exception as e:
            print(f"Error compressing history: {e}")
            # Fallback to direct truncation if LLM fails
            return messages[-max_messages:]

    def save_history(self, messages: List[BaseMessage]):
        """Saves conversation history to the local JSON file."""
        try:
            # Compress before saving if necessary
            messages = self._compress_history(messages)
            
            data = messages_to_dict(messages)
            with open(self.session_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving session {self.session_id}: {e}")
            
    def append_messages(self, new_messages: List[BaseMessage]):
        """Appends new messages to the existing history and compresses if necessary."""
        history = self.load_history()
        history.extend(new_messages)
        self.save_history(history)
