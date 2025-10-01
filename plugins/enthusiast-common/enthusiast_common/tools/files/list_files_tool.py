import json

from enthusiast_common.tools import BaseFileTool


class FileListTool(BaseFileTool):
    NAME = "file_listing_tool"
    DESCRIPTION = "It's tool for listing all available user's files/images. Use is always to determine file ID. Do not return ids to user use it only as tool input."
    ARGS_SCHEMA = None
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def run(self):
        files = self._injector.repositories.conversation.list_files(self._conversation_id)
        output = {"files": [{"filename": file.file.name.split("/")[-1], "file_id": file.pk} for file in files]}
        return f"Files found: {json.dumps(output)}"
