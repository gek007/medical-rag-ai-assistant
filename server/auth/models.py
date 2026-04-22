from typing import Literal

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    role: Literal["doctor", "user"]  # admin cannot be self-assigned via public signup
