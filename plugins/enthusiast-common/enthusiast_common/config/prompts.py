from __future__ import annotations

from enum import Enum
from typing import Union

from enthusiast_common.structures import BaseFileContent, BaseImageContent, TextContent
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self

TEXT_CONTENT_TYPE = "input_text"


class MessageRole(str, Enum):
    USER = "user"
    SYSTEM = "system"
    PLACEHOLDER = "placeholder"
    AI = "ai"


class Message(BaseModel):
    content: Union[str, list[TextContent | BaseFileContent | BaseImageContent]]
    role: MessageRole

    @field_validator("content", mode="after")
    def validate_content(cls, value: Union[str, list[TextContent | BaseFileContent | BaseImageContent]]):
        if isinstance(value, str):
            return [TextContent(text=value, type=TEXT_CONTENT_TYPE)]
        return value

    def to_chat_prompt_template(self):
        if self.role == MessageRole.PLACEHOLDER:
            placeholder_value = self.content[0].text
            return {"role": self.role.value, "content": placeholder_value}
        return self.model_dump(mode="json")


class PromptTemplateConfig(BaseModel):
    prompt_template: str
    input_variables: list[str]


class ChatPromptTemplateConfig(BaseModel):
    messages: list[Message]

    @model_validator(mode="before")
    def validate_messages(cls, values):
        messages = values.get("messages", [])

        # user_items = [message for message in messages if message.role == MessageRole.USER]
        # if len(user_items) > 1:
        #     raise ValueError("Only one message of type USER is allowed.")

        return values

    def to_chat_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([message.to_chat_prompt_template() for message in self.messages])

    def add_files_content(self, files_objects: list[BaseFileContent | BaseImageContent]) -> Self:
        user_message = None
        for message in self.messages:
            if message.role == MessageRole.USER:
                user_message = message
        if not user_message:
            raise ValueError("No user message was provided.")
        for file in files_objects:
            user_message.content.append(file)
        return self.model_copy(update={"messages": self.messages})
