from typing import List, Dict, Optional
from dataclasses import dataclass, field
import datetime

@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

class InMemoryHistoryManager:
    """
    Manages chat history in memory using a dictionary.
    Implements a Sliding Window strategy.
    """
    def __init__(self, max_history_length: int = 10):
        # Storage format: {session_id: List[ChatMessage]}
        self._store: Dict[str, List[ChatMessage]] = {}
        self.max_history_length = max_history_length

    def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Retrieve history for a session."""
        return self._store.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to history and enforce sliding window."""
        if session_id not in self._store:
            self._store[session_id] = []
        
        # Add new message
        message = ChatMessage(role=role, content=content)
        self._store[session_id].append(message)
        
        # Enforce Sliding Window (Keep only last N messages)
        if len(self._store[session_id]) > self.max_history_length:
            self._store[session_id] = self._store[session_id][-self.max_history_length:]

    def clear_session(self, session_id: str):
        """Clear history for a specific session."""
        if session_id in self._store:
            del self._store[session_id]

    def get_context_string(self, session_id: str) -> str:
        """
        Format history as a string for LLM Context.
        Format:
        User: ...
        Assistant: ...
        """
        messages = self.get_messages(session_id)
        if not messages:
            return ""
            
        formatted_history = []
        for msg in messages:
            role_title = "User" if msg.role == "user" else "Assistant"
            formatted_history.append(f"{role_title}: {msg.content}")
            
        return "\n".join(formatted_history)
