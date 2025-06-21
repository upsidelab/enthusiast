---
sidebar_position: 2
---

# Add Custom Tools

Occasionally, it may be necessary to extend Enthusiast with custom tools.
Tools in Enthusiast utilize Langchain's interface for creating tools.

Common reasons for implementing custom tools include:
1. Incorporating data from external sources into the context for generating responses
2. Enhancing the agent's capabilities with custom functionalities

## Example: Creating a custom plugin for verifying correctness of a statement

In this example, we will develop a tool that verifies the accuracy of a user-provided statement, utilizing the product catalog and RAG. This tool can help customer support agents to validate their responses before sending them to customers.

### Create a new package

We recommend keeping your custom tools in a separate package. This will keep it outside of Enthusiast's codebase, and will make it easy to upgrade the core of the system in the future.

Let's use Poetry and create a new library:

```shell
poetry new my-custom-verification-tool
cd my-custom-verification-tool
```

Add `enthusiast-common` as a dependency, to access the required interfaces:

```shell
poetry add enthusiast-common
```

### Implement a custom tool

Next, implement your custom tool. Let's create a file named `tool.py` that contains a class that inherits from `CustomTool` interface:

```python title="my-custom-verification-tool/my_custom_verification_tool/tool.py"
from pydantic import BaseModel
from enthusiast_common import CustomTool
from agent.retrievers import DocumentRetriever
from agent.retrievers import ProductRetriever
from agent.registries.language_models import LanguageModelRegistry

VERIFY_CONTENT_PROMPT = """
    Based on the following documents delimited by three backticks
    ```{document_context}```
    and the following products delimited by three backticks
    ```{product_context}```
    verify whether the following statement is correct
    ```{query}```
"""

class MyCustomVerificationToolInput(BaseModel):
    statement: str

class MyCustomVerificationTool(CustomTool):
    name: str = "verification_tool"
    description: str = "use this tool to verify whether a statement provided by user is correct"
    args_schema: Type[BaseModel] = MyCustomVerificationToolInput
    return_direct: bool = True

    def __init__(self, data_set, chat_model, **kwargs):
        super().__init__(data_set=data_set, chat_model=chat_model, **kwargs)

    def _run(self, statement: str):
        document_retriever = DocumentRetriever(data_set=self.data_set)
        relevant_documents = document_retriever.find_documents_matching_query(query)
        relevant_products = ProductRetriever(data_set=self.data_set).find_products_matching_query(query)

        document_context = ' '.join([x.content for x in relevant_documents])
        product_context = serializers.serialize("json", relevant_products)

        prompt = PromptTemplate.from_template(VERIFY_CONTENT_PROMPT)
        llm = LanguageModelRegistry().provider_for_dataset(self.data_set).provide_language_model()
        chain = prompt | llm

        return chain.invoke({
            "query": statement,
            "document_context": document_context,
            "product_context": product_context
        }).content
```

Finally, export the tool class in the ``__init__.py`` file

```python title="my-custom-verification-tool/my_custom_verification_tool/__init__.py"
from .tool import MyCustomVerificationTool as MyCustomVerificationTool 
```



Finally, register the custom tool in the ``settings.py`` file:

```python title="server/pecl/settings.py"
AGENT_TOOLS = {
    ...
    "Verification": "my_custom_verification_tool.MyCustomVerificaitonTool",
}
```
:::important
Restart the server to load the new tool.
:::

From now, when the agent detects that user's request is related to verifying their statement, it will use your new tool to fulfill that request.
The agent can have multiple tools enabled at the same time.

## Further reading

- [Interface definitions in the enthusiast-common package](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/interfaces.py)
- [Default tool implementation](https://github.com/upsidelab/enthusiast/blob/main/server/agent/tools/create_answer_tool.py)
