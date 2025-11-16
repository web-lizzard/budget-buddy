from typing import Literal

from pydantic import BaseModel

TOKEN_TYPE = Literal["bearer"]


class LoginDTO(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: TOKEN_TYPE = "bearer"
