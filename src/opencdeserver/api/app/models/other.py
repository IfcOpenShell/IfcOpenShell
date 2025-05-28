from __future__ import annotations
from pydantic import BaseModel
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: List[str] = []
    expires: str | None = None


class LoginReq(BaseModel):
    username: str
    password: str
