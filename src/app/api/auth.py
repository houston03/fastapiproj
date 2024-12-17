from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.app.database.database import get_db
from src.app.database.models import User as UserModel
from src.app.schemas.authuser import UserAuth
import os
import datetime
import bcrypt
import logging
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables")

if not isinstance(SECRET_KEY, str):
    SECRET_KEY = str(SECRET_KEY)

if len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY is too short")

logger.debug(
    f"SECRET_KEY: {SECRET_KEY}, type: {type(SECRET_KEY)}, len: {len(SECRET_KEY)}, repr: {repr(SECRET_KEY)}"
)
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Generated JWT Token: {encoded_jwt}")
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    try:
        logger.debug(f"Plain password: {plain_password}")
        logger.debug(f"Hashed password from DB: {hashed_password}")
        result = bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.exception(f"Ошибка в verify_password: {e}")
        return False


async def authenticate_user(username: str, password: str, db: AsyncSession):
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        result = await db.execute(
            select(UserModel).filter(UserModel.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user


@router.post("/token", response_model=UserAuth)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    try:
        user = await authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.username})
        user_data = {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
        }
        return {"access_token": access_token, "token_type": "bearer", "user": user_data}
    except Exception as e:
        logger.exception(f"Ошибка в login_for_access_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
