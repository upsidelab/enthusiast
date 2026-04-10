from datetime import datetime

from agent.models.conversation import ConversationFile
from agent.models.message import Message


class ConversationFileMessageService:
    """Creates the FILE message that surfaces an attached file in the conversation history."""

    def create_for_file(self, conversation_file: ConversationFile) -> Message:
        """Create a FILE message for the given ConversationFile.

        Args:
            conversation_file: The already-persisted ConversationFile to create a message for.

        Returns:
            The newly created Message record.
        """
        file_name = conversation_file.file.name
        return Message.objects.create(
            conversation_id=conversation_file.conversation_id,
            created_at=datetime.now(),
            type=Message.MessageType.FILE,
            file_name=file_name.rsplit(".", 1)[0],
            file_type=file_name.rsplit(".", 1)[-1],
            text=f"Uploaded {file_name} with id: {conversation_file.pk}",
        )
