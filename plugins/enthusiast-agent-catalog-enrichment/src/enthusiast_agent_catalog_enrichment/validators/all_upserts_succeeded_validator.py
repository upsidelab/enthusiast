import json
from typing import Optional

from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ExecutionInputType,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolResultMemory

from enthusiast_agent_catalog_enrichment.tools.upsert_product_details_tool import UpsertProductDetailsTool


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

        tool_results = tool_result_memory.get_results(self._TOOL_NAME)
        if not tool_results:
            return ValidatorSuccessResponse()

        failed_skus: list[str] = []

        for tool_result in tool_results:
            try:
                outcomes: dict[str, bool] = json.loads(tool_result.result)
            except (json.JSONDecodeError, TypeError):
                continue
            failed_skus.extend(sku for sku, success in outcomes.items() if not success)

        if not failed_skus:
            return ValidatorSuccessResponse()

        skus_list = ", ".join(failed_skus)
        return ValidatorFailureResponse(
            feedback=(
                f"The following products failed to upsert: {skus_list}. "
                f"Please review the product data and retry the upsert."
            ),
            retry_needed=True,
        )
