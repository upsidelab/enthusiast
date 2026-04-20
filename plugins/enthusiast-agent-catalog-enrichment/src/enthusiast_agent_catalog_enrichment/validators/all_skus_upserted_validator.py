import json
from typing import Optional

from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolResultMemory

from enthusiast_agent_catalog_enrichment.execution_input import CatalogEnrichmentAgenticExecutionInput
from enthusiast_agent_catalog_enrichment.tools.upsert_product_details_tool import UpsertProductDetailsTool


class AllSkusUpsertedValidator(BaseExecutionValidator):
    _TOOL_NAME = UpsertProductDetailsTool.NAME

    def validate(
        self,
        response: str,
        execution_input: CatalogEnrichmentAgenticExecutionInput,
        tool_result_memory: Optional[ToolResultMemory] = None,
    ) -> ValidatorResponse:
        if not execution_input.skus:
            return ValidatorSuccessResponse()

        attempted_skus: set[str] = set()
        if tool_result_memory:
            for tool_result in tool_result_memory.get_results(self._TOOL_NAME):
                try:
                    outcomes: dict[str, bool] = json.loads(tool_result.result)
                    attempted_skus.update(outcomes.keys())
                except (json.JSONDecodeError, TypeError):
                    continue

        missing_skus = [sku for sku in execution_input.skus if sku not in attempted_skus]
        if not missing_skus:
            return ValidatorSuccessResponse()

        skus_list = ", ".join(missing_skus)
        return ValidatorFailureResponse(
            feedback=(
                f"The following SKUs were not upserted: {skus_list}. "
                f"Search the available resources for product data on these specific SKUs. "
                f"If you find the data, retry the upsert for all products. "
                f"If the data is not present in any available resource, stop the execution."
            ),
            retry_needed=True,
        )
