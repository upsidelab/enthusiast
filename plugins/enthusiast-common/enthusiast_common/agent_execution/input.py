from pydantic import BaseModel


class ExecutionInputType(BaseModel):
    model_config = {"extra": "forbid"}