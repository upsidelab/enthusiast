import json

from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from enthusiast_agent_catalog_web_import.execution_input import CatalogWebImportExecutionInput


class AllUrlsCoveredValidator(BaseExecutionValidator):
    """Ensures every input URL appears in the agent's final response.

    Guards against the agent silently skipping URLs — if a URL from the execution
    input is absent from the response JSON keys, the agent is asked to process the
    missing ones and retry.
    """

    def validate(
        self,
        response: str,
        execution_input: CatalogWebImportExecutionInput,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        try:
            result = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            return ValidatorSuccessResponse()

        missing_urls = [url for url in execution_input.urls if url not in result]
        if not missing_urls:
            return ValidatorSuccessResponse()

        urls_list = "\n".join(f"- {url}" for url in missing_urls)
        return ValidatorFailureResponse(
            feedback=(
                f"The following URLs were not processed:\n{urls_list}\n"
                "Scrape and upsert products from these URLs, then return the complete response "
                "including all originally requested URLs."
            ),
            retry_needed=True,
        )
