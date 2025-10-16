from enthusiast_common.tools import BaseFileTool
from pydantic import BaseModel, Field


class FileRetrievalToolInput(BaseModel):
    file_ids: str = Field(description="String with comma seperated file ids")
    action: str = Field(description="Full action description to perform on file/s.")


class FileRetrievalTool(BaseFileTool):
    NAME = "file_operation_tool"
    DESCRIPTION = "It's AI tool for perform action with file/s."
    ARGS_SCHEMA = FileRetrievalToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def run(self, file_ids: str, action: str):
        parsed_file_ids = file_ids.split(",")
        file_objects = self._injector.repositories.conversation.get_file_objects(self._conversation_id, parsed_file_ids)

        from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole

        chat_prompt_template_config = ChatPromptTemplateConfig(
            messages=[
                Message(
                    role=MessageRole.SYSTEM,
                    content=f"{action}",
                ),
                Message(role=MessageRole.USER, content=""),
            ]
        )
        llm_provider = self._llm_registry.provider_for_dataset(self._data_set_id)
        llm_file_objects = llm_provider.prepare_files_objects(file_objects)
        chat_prompt_template_config.add_files_content(llm_file_objects)
        chat_prompt_template = chat_prompt_template_config.to_chat_prompt_template()
        messages = chat_prompt_template.format_messages()

        response = self._llm.invoke(messages)
        return f"{response}"
