from enthusiast_agent_catalog_enrichment.tools import UpsertProductDetailsTool
from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ExecutionInputType,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad


class UpsertToolCalledValidator(BaseExecutionValidator):
    """Ensures the upsert tool was actually called during the execution attempt.

    Guards against the agent producing a valid JSON response without ever invoking
    the upsert_product_properties tool — in which case no products were written to
    the catalog despite a seemingly successful response.
    """

    def validate(
        self,
        response: str,
        _execution_input: ExecutionInputType,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        entry = tool_scratchpad.read(UpsertProductDetailsTool.NAME)
        if entry is None:
            return ValidatorFailureResponse(
                feedback=(
                    "You returned a response but did not call the upsert tool. "
                    "Scrape the provided URLs, extract all product data, and call "
                    "the upsert tool before responding."
                ),
                retry_needed=True,
            )
        return ValidatorSuccessResponse()
