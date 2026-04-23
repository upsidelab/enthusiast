from typing import Optional

from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ExecutionInputType,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolResultMemory

from enthusiast_agent_catalog_enrichment.tools.upsert_product_details_tool import (
    UpsertMemoryEntry,
    UpsertProductDetailsTool,
)


class AllUpsertsSucceededValidator(BaseExecutionValidator):
    _TOOL_NAME = UpsertProductDetailsTool.NAME

    def validate(
        self,
        response: str,
        _execution_input: ExecutionInputType,
        tool_result_memory: Optional[ToolResultMemory] = None,
    ) -> ValidatorResponse:
        if tool_result_memory is None:
            return ValidatorSuccessResponse()

        entry: UpsertMemoryEntry | None = tool_result_memory.get_tool_result(self._TOOL_NAME)
        if entry is None:
            return ValidatorSuccessResponse()

        failed_skus = [sku for sku, success in entry.items() if not success]
        if not failed_skus:
            return ValidatorSuccessResponse()

        return ValidatorFailureResponse(
            feedback=(
                f"The following products failed to upsert: {', '.join(failed_skus)}. "
                f"Please review the product data and retry the upsert."
            ),
            retry_needed=True,
        )
