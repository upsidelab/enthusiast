from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from celery import Task, shared_task
from channels.layers import get_channel_layer
from django.core.files.base import ContentFile
from django.utils import timezone

from agent.conversation import ConversationManager
from agent.core.callbacks import BaseWebSocketHandler
from agent.execution.registry import AgentExecutionRegistry
from agent.file_service import FileService
from agent.models import Message
from agent.models.agent_execution import AgentExecution
from agent.models.conversation import Conversation, ConversationFile
from agent.serializers.conversation import ConversationFileSerializer
from pecl import settings


class SaveMessageOnFailureTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        conversation_id = kwargs.get("conversation_id")
        data_set_id = kwargs.get("data_set_id")
        user_id = kwargs.get("user_id")
        message = kwargs.get("message")

        Message.objects.create(
            conversation_id=conversation_id,
            created_at=datetime.now(),
            type=Message.MessageType.HUMAN,
            text=message,
            answer_failed=True,
        )

        manager = ConversationManager()
        manager.record_error(conversation_id, user_id, data_set_id, exc)
        ws_handler = BaseWebSocketHandler(conversation_id=conversation_id)
        ws_handler.send_message({"type": "chat_message", "event": "error", "output": manager.DEFAULT_ERROR_MESSAGE})


@shared_task(base=SaveMessageOnFailureTask, bind=True, max_retries=3)
def respond_to_user_message_task(
    self, conversation_id: int, data_set_id: int, user_id: int, message: str, streaming: bool
):
    manager = ConversationManager()
    try:
        answer = manager.respond_to_user_message(
            conversation_id=conversation_id,
            data_set_id=data_set_id,
            user_id=user_id,
            message=message,
            streaming=streaming,
        )
        if streaming:
            channel_layer = get_channel_layer()
            group_name = f"conversation_{conversation_id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat_message",
                    "event": "message_created",
                    "answer_id": answer.id,
                },
            )
        return {"conversation_id": conversation_id, "message_id": answer.id}
    except Exception:
        self.retry(countdown=1)


@shared_task
def process_file_upload_task(conversation_id: int, file_content: bytes, filename: str, content_type: str):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        django_file = ContentFile(file_content, name=filename)
        file_category = "image" if content_type.startswith("image/") else "file"

        obj = ConversationFile(
            conversation=conversation,
            file=django_file,
            content_type=content_type,
            file_category=file_category,
            llm_content=FileService(django_file, content_type).process() or "",
        )

        obj.save()

        serializer = ConversationFileSerializer(obj)

        return {
            "status": "SUCCESS",
            "conversation_id": conversation_id,
            "uploaded_file": serializer.data,
            "file_id": obj.id,
        }

    except Conversation.DoesNotExist:
        return {"status": "FAILURE", "error": f"Conversation {conversation_id} not found"}
    except Exception as e:
        return {"status": "FAILURE", "error": str(e)}


@shared_task(max_retries=0)
def run_agent_execution_task(execution_id: int):
    execution = AgentExecution.objects.get(pk=execution_id)
    execution.mark_in_progress()

    try:
        registry = AgentExecutionRegistry()
        execution_cls = registry.get_by_key(execution.execution_type)
        input_data = execution_cls.INPUT_TYPE(**execution.input)
        result = execution_cls().run(input_data)
        execution.mark_finished(result=result.output)
    except Exception as exc:
        execution.mark_failed(
            failure_code=type(exc).__name__,
            failure_explanation=str(exc),
        )
        raise


@shared_task
def clean_uploaded_files():
    ConversationFile.objects.filter(
        created_at__lt=timezone.now() - timedelta(hours=settings.UPLOADED_FILE_RETENTION_PERIOD_HOURS)
    ).delete()
