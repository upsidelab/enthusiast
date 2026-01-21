from pydantic import BaseModel


class BaseContent(BaseModel):
    type: str
