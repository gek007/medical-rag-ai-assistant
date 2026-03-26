from typing import Optional

from pydantic import BaseModel


class SignupRequest(BaseModel):
    username: str
    password: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str
