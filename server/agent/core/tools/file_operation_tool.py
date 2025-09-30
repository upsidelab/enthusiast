import logging

from enthusiast_common.tools import BaseLLMTool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FileOperationToolInput(BaseModel):
    file_id: str = Field(description="File id.")
    action: str = Field(description="Action to take on file.")


class FileOperationTool(BaseLLMTool):
    NAME = "file_operation_tool"
    DESCRIPTION = "It's tool for perform action with file."
    ARGS_SCHEMA = FileOperationToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def run(self, file_id, action):
        if self._conversation_id is None:
            return "There is no files available"
        file = self._injector.repositories.conversation.get_files(self._conversation_id).filter(id=file_id).first()
        content = file.llm_content

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
