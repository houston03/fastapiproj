from pydantic import BaseModel


class UserAuth(BaseModel):
    access_token: str
    token_type: str
    user: dict
