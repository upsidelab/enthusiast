from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ValidatorFailureResponse,
    ValidatorResponse,
    ValidatorSuccessResponse,
)
from enthusiast_common.agentic_execution.memory import ToolScratchpad

from enthusiast_agent_catalog_web_import.execution_input import CatalogWebImportExecutionInput
from enthusiast_agent_catalog_web_import.tools.scrape_product_tool import ScrapeMemoryEntry, ScrapeProductTool


class AllUrlsFetchSuccessfulValidator(BaseExecutionValidator):
    """Ensures every input URL was scraped and the fetch succeeded.

    Reads the ToolScratchpad entry recorded by ScrapeProductTool. If the tool was
    never called, the agent is asked to retry. If any URL fetch failed with a network
    or internal error, the agent is asked to retry those URLs.
    """

    _TOOL_NAME = ScrapeProductTool.NAME

    def validate(
        self,
        response: str,
        execution_input: CatalogWebImportExecutionInput,
        tool_scratchpad: ToolScratchpad,
    ) -> ValidatorResponse:
        entry: ScrapeMemoryEntry | None = tool_scratchpad.read(self._TOOL_NAME)
        if entry is None:
            return ValidatorFailureResponse(
                feedback=(
                    "You returned a response but did not call the scrape tool. "
                    "Call the scrape tool for all provided URLs before responding."
                ),
                retry_needed=True,
            )

        failed_urls = [url for url, success in entry.items() if not success]
        if not failed_urls:
            return ValidatorSuccessResponse()

        urls_list = "\n".join(f"- {url}" for url in failed_urls)
        return ValidatorFailureResponse(
            feedback=(
                f"The following URLs could not be fetched:\n{urls_list}\n"
                "Retry scraping these URLs. If they remain unreachable, stop the execution."
            ),
            retry_needed=True,
        )
