from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    ExecutionConversationInterface,
    ExecutionInputType,
)


class ProductWebScraperExecutionInput(ExecutionInputType):
    """Input for the product web scraper agentic execution."""

    urls: list[str]
    additional_instructions: str | None = None


class ProductWebScraperExecutionDefinition(BaseAgenticExecutionDefinition):
    """Agentic execution definition for the product web scraper agent.

    Scrapes product data from the provided URLs and upserts it into the catalog.
    """

    EXECUTION_KEY = "product-web-scraper"
    AGENT_KEY = "enthusiast-agent-product-web-scraper"
    NAME = "Product Web Scraper"
    INPUT_TYPE = ProductWebScraperExecutionInput

    def execute(
        self,
        input_data: ProductWebScraperExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        urls_list = "\n".join(f"- {url}" for url in input_data.urls)
        message = f"Scrape and upsert the following product pages:\n{urls_list}"
        if input_data.additional_instructions:
            message += f"\n\n{input_data.additional_instructions}"
        return conversation.ask(message)
