from enthusiast_common.tools import BaseFileTool
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field


class FileRetrievalToolInput(BaseModel):
    file_ids: str = Field(description="String with comma seperated file ids")
    action: str = Field(description="Describe what you want to know about specific file in details.")


class FileRetrievalTool(BaseFileTool):
    NAME = "file_operation_tool"
    DESCRIPTION = "It's AI tool for perform action with file/s."
    ARGS_SCHEMA = FileRetrievalToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def run(self, file_ids: str, action: str):
        parsed_file_ids = file_ids.split(",")
        file_objects = self._injector.repositories.conversation.get_file_objects(self._conversation_id, parsed_file_ids)

        llm_provider = self._llm_registry.provider_for_dataset(self._data_set_id)
        llm_file_objects = llm_provider.prepare_files_objects(file_objects)

        messages = [
            SystemMessage(content=action),
            HumanMessage(content=[file_obj.model_dump(mode="json") for file_obj in llm_file_objects]),
        ]

        response = self._llm.invoke(messages).content
        return f"{response}"
