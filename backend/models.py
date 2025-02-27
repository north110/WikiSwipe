from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    interactions = relationship("UserInteraction", back_populates="user")

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    wikipedia_id = Column(String, unique=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    categories = Column(String)  # You can store comma-separated values or JSON
    url = Column(String)
    last_fetched = Column(DateTime, default=datetime.datetime.utcnow)
    interactions = relationship("UserInteraction", back_populates="article")

class UserInteraction(Base):
    __tablename__ = 'user_interactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey('articles.id'))
    interaction_type = Column(String, default='like')
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="interactions")
    article = relationship("Article", back_populates="interactions")

# Create an engine and initialize the SQLite database
engine = create_engine('sqlite:///wiki.db')
Base.metadata.create_all(engine)
