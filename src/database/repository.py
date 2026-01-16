from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.database.models import ChatSession, ChatMessage
import datetime

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, title: str = "New Chat", meta: Dict[str, Any] = None) -> ChatSession:
        if meta is None:
            meta = {}
        session = ChatSession(title=title, metadata_=meta)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_recent_sessions(self, limit: int = 10, offset: int = 0) -> List[ChatSession]:
        return (
            self.db.query(ChatSession)
            .order_by(desc(ChatSession.updated_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_session_title(self, session_id: str, title: str) -> Optional[ChatSession]:
        session = self.get_session(session_id)
        if session:
            session.title = title
            self.db.commit()
            self.db.refresh(session)
        return session
        
    def delete_session(self, session_id: str):
        session = self.get_session(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()

    def delete_all_sessions(self) -> int:
        num_deleted = self.db.query(ChatSession).delete()
        self.db.commit()
        return num_deleted

    def add_message(self, session_id: str, role: str, content: str,
                    sources: List[Dict] = None, standalone_query: str = None) -> ChatMessage:
        if sources is None:
            sources = []

        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            standalone_query=standalone_query
        )
        self.db.add(msg)
        
        # Manually update session timestamp
        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(self, session_id: str) -> List[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
