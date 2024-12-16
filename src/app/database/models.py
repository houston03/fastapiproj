from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from src.app.database.database import Base
from sqlalchemy.dialects.postgresql import TSVECTOR


class Article(Base):
    __tablename__ = "articles"
    article_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    summary_1 = Column(Text)
    summary_2 = Column(Text)
    publication_date = Column(DateTime(timezone=True), server_default="NOW()")
    author_id = Column(
        Integer, ForeignKey("users.user_id")
    )
    author = relationship("User", back_populates="articles")  # Связь с User
    tsv_content = Column(TSVECTOR)


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)
    phone_number = Column(String(20))
    articles = relationship("Article", back_populates="author")
