import json
import logging

from enthusiast_common.tools import BaseLLMTool

logger = logging.getLogger(__name__)

#
# class OrderPlacementToolInput(BaseModel):
#     product_ids: str = Field(description="comma separated string with products entry_ids")


class FileListTool(BaseLLMTool):
    NAME = "file_listing_tool"
    DESCRIPTION = "It's tool for listing all available files. Do not return ids to user."
    ARGS_SCHEMA = None
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def run(self):
        if self._conversation_id is None:
            return "There is no files available"
        files = self._injector.repositories.conversation.get_files(self._conversation_id)
        output = {file.file.name.split("/")[-1]: file.pk for file in files}
        return f"files found: {json.dumps(output)}"
