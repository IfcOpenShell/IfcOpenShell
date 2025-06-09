from __future__ import annotations
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
    expires: str | None = None


class LoginReq(BaseModel):
    username: str
    password: str
