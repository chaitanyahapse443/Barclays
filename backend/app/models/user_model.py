from pydantic import BaseModel
from typing import List

class User(BaseModel):
    user_id: str
    username: str
    roles: List[str] = []
