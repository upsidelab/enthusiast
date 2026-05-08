from enthusiast_agent_catalog_enrichment.tools.upsert_product_details_tool import (
    UpsertMemoryEntry,
    UpsertProductDetailsTool,
)
from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ExecutionInputType,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad


class AllUpsertsSucceededValidator(BaseExecutionValidator):
    """Validates that the upsert tool was called and all product upserts succeeded.

    If the tool was never called, the agent is asked to retry — it may have returned
    a response without ever invoking the upsert tool. If some products failed to upsert,
    the agent is asked to review the data and retry those products.
    """

    _TOOL_NAME = UpsertProductDetailsTool.NAME

    def validate(
        self,
        response: str,
        _execution_input: ExecutionInputType,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        entry: UpsertMemoryEntry | None = tool_scratchpad.read(self._TOOL_NAME)
        if entry is None:
            return ValidatorFailureResponse(
                feedback=(
                    "You returned a response but did not call the upsert tool. "
                    "Scrape the provided URLs, extract all product data, and call "
                    "the upsert tool before responding."
                ),
                retry_needed=True,
            )

        failed_skus = [sku for sku, success in entry.items() if not success]
        if not failed_skus:
            return ValidatorSuccessResponse()

        return ValidatorFailureResponse(
            feedback=(
                f"The following products failed to upsert: {', '.join(failed_skus)}. "
                "Please review the product data and retry the upsert."
            ),
            retry_needed=True,
        )
