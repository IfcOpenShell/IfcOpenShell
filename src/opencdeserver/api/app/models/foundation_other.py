from __future__ import annotations
from pydantic import BaseModel


class TokenRequest(BaseModel):
    grant_type: str | None = None


class UserInfo(BaseModel):
    username: str
    scope: str


class TokenInfo(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    expires_in: str | None = None
