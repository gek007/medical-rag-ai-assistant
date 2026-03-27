from typing import Literal

from pydantic import BaseModel


class SignupRequest(BaseModel):
    username: str
    password: str
    role: Literal["doctor", "admin", "user"]


class LoginRequest(BaseModel):
    username: str
    password: str
