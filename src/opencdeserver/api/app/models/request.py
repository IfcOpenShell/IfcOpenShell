from __future__ import annotations
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UserInDB(User):
    hashed_password: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
