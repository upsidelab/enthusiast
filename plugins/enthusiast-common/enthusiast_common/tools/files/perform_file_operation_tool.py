from enthusiast_common.tools import BaseFileTool
from pydantic import BaseModel, Field

class FileRetrievalToolInput(BaseModel):
    file_ids: str = Field(description="String with comma separated file ids")
    schema_as_json: str = Field(description="JSON parsable string of entity properties to be extracted from files")


class SCHEMA(BaseModel):
    products: str = Field(description='extracted products as JSON list')
    contains_more: bool = Field(description='whether or not there are more products in the file to extract')


SYSTEM_PROMPT_TEMPLATE = """
    You are a structured information extraction engine for furniture catalogs.

    GOAL
    Extract ALL products and ALL size variants from the provided catalog PDF and output them strictly as JSON using the schema below.

    CRITICAL RULES
    - Do NOT invent data.
    - If a field is missing, omit it.
    - Output JSON only. No extra text.
    - EACH SIZE VARIANT MUST BE A SEPARATE PRODUCT ENTRY.

    PRIMARY DATA SOURCE (IMPORTANT)
    Dimensions diagrams are the PRIMARY source of variant and size information.
    You MUST carefully analyze ALL dimension diagrams for each product.

    CATALOG STRUCTURE
    - Each product has a main SKU shown next to the product title.
    - Size variants are usually shown in dimension diagrams.
    - Variant SKUs follow the format: "MAIN_SKU/SUBNUMBER" (e.g. "1000/100").
    - Variant SKUs are often placed above the dimension diagrams.
    - A single product may have multiple diagrams, each representing a different size variant.

    DIMENSIONS EXTRACTION (MANDATORY)
    - Most products include a furniture dimensions diagram.
    - Diagrams show simplified furniture drawings with dimension lines.
    - Dimension values are given in centimeters.
    - Extract all available dimensions (e.g. width, length, depth, height).
    - Populate schema dimension fields using ONLY diagram data when available.
    - If a product has a dimension diagram and no dimensions are extracted, the output is considered incorrect.
    
    COMPOSITION DIAGRAMS (IMPORTANT EXCLUSION)
    - Some diagrams represent product compositions, NOT size variants.
    - These diagrams do NOT have a SKU above them.
    - They are typically labeled with numbers like "1.", "2.", etc. above the diagram.
    - Composition diagrams MUST be ignored.
    - Do NOT extract variants or dimensions from composition diagrams.

    VARIANT HANDLING
    - If multiple diagrams or dimension sets exist for a product:
      - Treat each as a separate variant.
      - Assign the correct variant SKU if present.
      - Copy shared attributes from the main product if needed.
    - Do NOT collapse variants into a single entry.

    OUTPUT FORMAT
    Return the extracted data strictly following this JSON schema:
    {schema_as_json}
"""

class FileRetrievalTool(BaseFileTool):
    NAME = "file_operation_tool"
    DESCRIPTION = "It's AI tool for perform action with file/s."
    ARGS_SCHEMA = FileRetrievalToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def run(self, file_ids: str, schema_as_json: str):
        parsed_file_ids = file_ids.split(",")
        file_objects = self._injector.repositories.conversation.get_file_objects(self._conversation_id, parsed_file_ids)

        from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole

        full_products = ''
        more_to_extract = True
        file_added = False
        messages = [
            Message(role=MessageRole.SYSTEM,content=SYSTEM_PROMPT_TEMPLATE),
            Message(role=MessageRole.USER, content="")
        ]


        while more_to_extract:
            print("Asking agent to extract data")
            chat_prompt_template_config = ChatPromptTemplateConfig(messages=messages)
            if not file_added:
                llm_provider = self._llm_registry.provider_for_dataset(self._data_set_id)
                llm_file_objects = llm_provider.prepare_files_objects(file_objects)
                chat_prompt_template_config.add_files_content(llm_file_objects)
                file_added = True
            chat_prompt_template = chat_prompt_template_config.to_chat_prompt_template()
            prompt = chat_prompt_template.format_messages(schema_as_json=schema_as_json)
            response = self._llm.with_structured_output(SCHEMA).invoke(prompt)
            print(response)

            response_message = f"""
            {{ "products": {response.products}, "contains_more": {response.contains_more} }}
            """.replace("{", "{{").replace("}", "}}")

            messages.append(Message(role=MessageRole.AI, content=response_message))
            messages.append(Message(role=MessageRole.USER, content="return the remaining files"))

            full_products = full_products + response.products
            more_to_extract = response.contains_more


        return f"{full_products}"
