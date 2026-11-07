import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class SessionCreate(BaseModel):
    title: str


class SearchSessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class QueryCreate(BaseModel):
    prompt: str


class QueryOut(BaseModel):
    id: int
    prompt: str
    response: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class SearchSessionDetailOut(SearchSessionOut):
    queries: list[QueryOut] = []

    model_config = ConfigDict(from_attributes=True)