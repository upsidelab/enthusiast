from enthusiast_agent_tool_calling import BaseToolCallingAgent
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field, Json


class InvoiceScanningAgentPromptInput(RequiredFieldsModel):
    output_format: Json = Field(
        title="Output format",
        description="Output format of the extracted data",
        default='{"invoice_number": "string", "issued_at": "string", "supplier_name": "string", "gross_amount": "number"}',
    )


class InvoiceScanningAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-invoice-scanning"
    NAME = "Invoice Scanning"
    PROMPT_INPUT = InvoiceScanningAgentPromptInput
    FILE_UPLOAD = True

    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        agent_output = agent_executor.invoke(
            {"input": input_text, "data_format": self.PROMPT_INPUT.output_format}, config=self._build_invoke_config()
        )
        return agent_output["output"]
