from typing import Optional

from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolResultMemory

from enthusiast_agent_catalog_enrichment.execution_input import CatalogEnrichmentAgenticExecutionInput
from enthusiast_agent_catalog_enrichment.tools.upsert_product_details_tool import (
    UpsertMemoryEntry,
    UpsertProductDetailsTool,
)


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
            entry: UpsertMemoryEntry | None = tool_result_memory.get_tool_result(self._TOOL_NAME)
            if entry:
                attempted_skus.update(entry.keys())

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
