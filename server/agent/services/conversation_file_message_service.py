from datetime import datetime

from agent.models.conversation import ConversationFile
from agent.models.message import Message


class ConversationFileMessageService:
    @staticmethod
    def create_for_file(conversation_file: ConversationFile) -> Message:
        file_name = conversation_file.file.name
        return Message.objects.create(
            conversation_id=conversation_file.conversation_id,
            created_at=datetime.now(),
            type=Message.MessageType.FILE,
            file_name=file_name.rsplit(".", 1)[0],
            file_type=file_name.rsplit(".", 1)[-1],
            text=f"Uploaded {file_name} with id: {conversation_file.pk}",
        )
