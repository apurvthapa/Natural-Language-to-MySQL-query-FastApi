from pydantic import BaseModel


class input(BaseModel):
    user_query: str
