from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.app.schemas.post import ArticleCreate, Article
from src.app.database.database import get_db
from src.app.database.models import Article as ArticleModel
from src.app.api.auth import get_current_user
from src.app.schemas.user import User
import datetime
import logging
from sqlalchemy import func

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Article)
async def create_article(
    article: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(f"Received article data: {article}")
    logger.debug(f"Current user: {current_user}")

    if article.author_id <= 0:
        logger.error("author_id must be greater than 0")
        raise HTTPException(status_code=422, detail="author_id must be greater than 0")

    try:
        article_data = article.dict()
        article_data.pop("author_id", None)
        db_article = ArticleModel(
            **article_data,
            publication_date=datetime.datetime.utcnow(),
            author_id=current_user.user_id,
        )
        db.add(db_article)
        await db.commit()
        await db.refresh(db_article)
        logger.debug(f"Article created successfully: {db_article}")
        return db_article
    except Exception as e:
        logger.exception(f"Error occurred while creating article {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{article_id}", response_model=Article)
async def read_article(article_id: int, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Fetching article with ID: {article_id}")
    db_article = await db.get(ArticleModel, article_id)
    if db_article is None:
        logger.error(f"Article with ID {article_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    logger.debug(f"Article found: {db_article}")
    return db_article


@router.get("/search/")
async def search_articles(query: str, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(
            select(ArticleModel).where(
                ArticleModel.tsv_content.op("@@")(func.plainto_tsquery(query))
            )
        )
        articles = result.scalars().all()
    return articles
