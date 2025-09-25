from enthusiast_common.tools import BaseLLMTool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class FileOperationToolInput(BaseModel):
    file_ids: str = Field(description="String with comma seperated file ids")
    action: str = Field(description="Action to take on file.")


class FileOperationTool(BaseLLMTool):
    NAME = "file_operation_tool"
    DESCRIPTION = "It's tool for perform action with file."
    ARGS_SCHEMA = FileOperationToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def run(self, file_ids, action):
        parsed_file_ids = file_ids.split(",")
        self._injector.repositories.conversation.get_file_objects(self._conversation_id, parsed_file_ids)
        content = ""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", f"{action}"),
                (
                    "user",
                    [
                        {
                            "type": "file",
                            "file": {
                                "file_data": f"data:application/pdf;base64,{content}",
                                "filename": "test.pdf",
                            },
                        },
                    ],
                ),
            ]
        )
        messages = prompt.format_messages()

        response = self._llm.invoke(messages)
        return f"{response}"
