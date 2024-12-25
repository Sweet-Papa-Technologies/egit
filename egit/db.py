"""
Database management for eGit using SQLAlchemy
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DB_FILE

# Initialize SQLAlchemy
Base = declarative_base()
engine = create_engine(f'sqlite:///{DB_FILE}')
Session = sessionmaker(bind=engine)

class GitMessage(Base):
    """Model for storing Git messages and related information"""
    __tablename__ = 'git_messages'
    
    id = Column(Integer, primary_key=True)
    commit_hash = Column(String(40), unique=True)
    original_message = Column(Text)
    generated_message = Column(Text)
    command_type = Column(String(50))  # 'summarize', 'release_notes', etc.
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize the database"""
    Base.metadata.create_all(engine)

def save_message(commit_hash: str, original_message: str, generated_message: str, command_type: str):
    """Save a message to the database"""
    session = Session()
    try:
        message = GitMessage(
            commit_hash=commit_hash,
            original_message=original_message,
            generated_message=generated_message,
            command_type=command_type
        )
        session.add(message)
        session.commit()
    finally:
        session.close()

def get_message(commit_hash: str) -> Optional[GitMessage]:
    """Get a message from the database"""
    session = Session()
    try:
        return session.query(GitMessage).filter_by(commit_hash=commit_hash).first()
    finally:
        session.close()

def get_messages_by_type(command_type: str) -> List[GitMessage]:
    """Get all messages of a specific type"""
    session = Session()
    try:
        return session.query(GitMessage).filter_by(command_type=command_type).all()
    finally:
        session.close()
