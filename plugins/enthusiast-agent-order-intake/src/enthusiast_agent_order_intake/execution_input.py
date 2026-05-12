from enthusiast_common.agentic_execution import ExecutionInputType
from pydantic import BaseModel


class OrderItem(BaseModel):
    sku: str
    quantity: int


class OrderIntakeAgenticExecutionInput(ExecutionInputType):
    items: list[OrderItem]
    additional_instructions: str | None = None
