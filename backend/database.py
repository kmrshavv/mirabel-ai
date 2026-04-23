# database.py - Complete Database Management
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import json
import os
from typing import List, Optional, Dict, Any

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./mirabel.db")

# Engine configuration based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
else:  # PostgreSQL or other production databases
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============== MODELS ==============

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    preferences = Column(Text, default="{}")  # JSON storage
    total_conversations = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def get_preferences(self) -> Dict[str, Any]:
        """Parse preferences JSON to dict"""
        try:
            return json.loads(self.preferences) if self.preferences else {}
        except:
            return {}
    
    def set_preferences(self, prefs: Dict[str, Any]):
        """Set preferences from dict"""
        self.preferences = json.dumps(prefs)


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), default="New Chat", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    model_used = Column(String(100), default="llama3.2:3b", nullable=False)
    is_archived = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": self.message_count,
            "is_archived": self.is_archived
        }


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tokens_used = Column(Integer, default=0)  # Optional: track token usage
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tokens_used": self.tokens_used
        }


class ModelStats(Base):
    __tablename__ = "model_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, nullable=False)
    total_calls = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    avg_response_time_ms = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def update_stats(self, response_time_ms: int, tokens: int = 0):
        """Update statistics for this model"""
        self.total_calls += 1
        self.total_tokens += tokens
        # Weighted average for response time
        self.avg_response_time_ms = (
            (self.avg_response_time_ms * (self.total_calls - 1) + response_time_ms) 
            // self.total_calls
        )
        self.last_used = datetime.utcnow()


# ============== DATABASE MANAGER ==============

class DBManager:
    def __init__(self):
        self._session: Optional[Session] = None
    
    @property
    def db(self) -> Session:
        """Lazy loading of session"""
        if self._session is None:
            self._session = SessionLocal()
        return self._session
    
    def close(self):
        """Close the database session"""
        if self._session:
            self._session.close()
            self._session = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    # ========== USER OPERATIONS ==========
    
    def get_or_create_user(self, username: str = "default_user", email: str = None) -> User:
        """Get existing user or create new one"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                email=email,
                created_at=datetime.utcnow()
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> Optional[User]:
        """Update user preferences"""
        user = self.get_user(user_id)
        if user:
            user.set_preferences(preferences)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    # ========== CONVERSATION OPERATIONS ==========
    
    def create_conversation(self, user_id: int, title: str = "New Chat", 
                           model_used: str = "llama3.2:3b") -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            model_used=model_used,
            created_at=datetime.utcnow()
        )
        self.db.add(conversation)
        
        # Update user's conversation count
        user = self.get_user(user_id)
        if user:
            user.total_conversations += 1
        
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_user_conversations(self, user_id: int, limit: int = 20, 
                               include_archived: bool = False) -> List[Conversation]:
        """Get user's conversations, optionally filtering archived"""
        query = self.db.query(Conversation).filter(Conversation.user_id == user_id)
        
        if not include_archived:
            query = query.filter(Conversation.is_archived == False)
        
        return query.order_by(Conversation.updated_at.desc()).limit(limit).all()
    
    def update_conversation_title(self, conversation_id: int, title: str) -> Optional[Conversation]:
        """Update conversation title"""
        conv = self.get_conversation(conversation_id)
        if conv:
            conv.title = title
            self.db.commit()
            self.db.refresh(conv)
        return conv
    
    def archive_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Archive a conversation"""
        conv = self.get_conversation(conversation_id)
        if conv:
            conv.is_archived = True
            self.db.commit()
            self.db.refresh(conv)
        return conv
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation permanently"""
        conv = self.get_conversation(conversation_id)
        if conv:
            self.db.delete(conv)
            self.db.commit()
            return True
        return False
    
    # ========== MESSAGE OPERATIONS ==========
    
    def add_message(self, conversation_id: int, role: str, content: str, 
                   tokens_used: int = 0) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow(),
            tokens_used=tokens_used
        )
        self.db.add(message)
        
        # Update conversation timestamp and message count
        conv = self.get_conversation(conversation_id)
        if conv:
            conv.updated_at = datetime.utcnow()
            conv.message_count = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).count()
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_history(self, conversation_id: int, limit: int = 50) -> List[Message]:
        """Get conversation history, newest first but returned in chronological order"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).limit(limit).all()
        return messages
    
    def get_last_n_messages(self, conversation_id: int, n: int = 10) -> List[Message]:
        """Get last N messages for context window"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(n).all()
        return list(reversed(messages))
    
    def clear_conversation_messages(self, conversation_id: int) -> bool:
        """Clear all messages from a conversation"""
        deleted = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).delete()
        
        # Reset message count
        conv = self.get_conversation(conversation_id)
        if conv:
            conv.message_count = 0
            conv.updated_at = datetime.utcnow()
        
        self.db.commit()
        return deleted > 0
    
    # ========== MODEL STATS OPERATIONS ==========
    
    def update_model_stats(self, model_name: str, response_time_ms: int, tokens: int = 0):
        """Update model performance statistics"""
        stats = self.db.query(ModelStats).filter(
            ModelStats.model_name == model_name
        ).first()
        
        if not stats:
            stats = ModelStats(model_name=model_name)
            self.db.add(stats)
        
        stats.update_stats(response_time_ms, tokens)
        self.db.commit()
    
    def get_model_stats(self, model_name: str = None) -> Dict[str, Any]:
        """Get statistics for a specific model or all models"""
        if model_name:
            stats = self.db.query(ModelStats).filter(
                ModelStats.model_name == model_name
            ).first()
            return {
                "model_name": stats.model_name,
                "total_calls": stats.total_calls,
                "total_tokens": stats.total_tokens,
                "avg_response_time_ms": stats.avg_response_time_ms,
                "last_used": stats.last_used.isoformat() if stats.last_used else None
            } if stats else {}
        
        # Get all models stats
        stats_list = self.db.query(ModelStats).all()
        return {stats.model_name: {
            "total_calls": stats.total_calls,
            "total_tokens": stats.total_tokens,
            "avg_response_time_ms": stats.avg_response_time_ms,
            "last_used": stats.last_used.isoformat() if stats.last_used else None
        } for stats in stats_list}
    
    # ========== STATISTICS & UTILITIES ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        users_count = self.db.query(User).count()
        conversations_count = self.db.query(Conversation).count()
        messages_count = self.db.query(Message).count()
        
        # Get last activity
        last_message = self.db.query(Message).order_by(
            Message.created_at.desc()
        ).first()
        last_activity = last_message.created_at if last_message else None
        
        # Get active users (users with at least one conversation)
        active_users = self.db.query(User).join(Conversation).distinct().count()
        
        # Total tokens across all messages
        total_tokens = self.db.query(func.sum(Message.tokens_used)).scalar() or 0
        
        return {
            "users": {
                "total": users_count,
                "active": active_users
            },
            "conversations": conversations_count,
            "messages": messages_count,
            "total_tokens": total_tokens,
            "last_activity": last_activity.isoformat() if last_activity else None
        }
    
    def vacuum(self):
        """Optimize database (SQLite only)"""
        if DATABASE_URL.startswith("sqlite"):
            self.db.execute("VACUUM")
            self.db.commit()


# ============== INITIALIZATION ==============

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

def get_db() -> DBManager:
    """Dependency injection for FastAPI"""
    db = DBManager()
    try:
        yield db
    finally:
        db.close()


# Create global instance for backwards compatibility
db_manager = DBManager()

# Initialize on import
init_database()