from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    ExecutionInputType,
)


class CatalogWebImportExecutionInput(ExecutionInputType):
    """Input for the catalog web import agentic execution."""

    urls: list[str]
    additional_instructions: str | None = None


class CatalogWebImportExecutionDefinition(BaseAgenticExecutionDefinition):
    """Agentic execution definition for the catalog web import agent.

    Scrapes product data from the provided URLs and upserts it into the catalog.
    """

    EXECUTION_KEY = "catalog-web-import"
    AGENT_KEY = "enthusiast-agent-catalog-web-import"
    NAME = "Catalog Web Import"
    INPUT_TYPE = CatalogWebImportExecutionInput

    def execute(
        self,
        input_data: CatalogWebImportExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        urls_list = "\n".join(f"- {url}" for url in input_data.urls)
        message = f"Scrape and upsert the following product pages:\n{urls_list}"
        if input_data.additional_instructions:
            message += f"\n\n{input_data.additional_instructions}"
        return conversation.ask(message)
