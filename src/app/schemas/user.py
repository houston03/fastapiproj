from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: str | None = None


class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    phone_number: str | None = None

    class Config:
        from_attributes: True
