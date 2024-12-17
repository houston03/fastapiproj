from datetime import datetime
from pydantic import BaseModel
from src.app.schemas.user import User


class ArticleCreate(BaseModel):
    title: str
    category: str
    summary_1: str | None = None
    summary_2: str | None = None
    author_id: int


class Article(ArticleCreate):
    article_id: int
    publication_date: datetime
    author: User

    class Config:
        from_attributes = True
