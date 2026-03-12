from celery import Task, shared_task
from enthusiast_common.agent_execution import ExecutionConversationInterface, ExecutionFailureCode
from enthusiast_common.agents import ConfigType

from agent.conversation import ConversationManager
from agent.execution.registry import AgentExecutionRegistry
from agent.models.agent_execution import AgentExecution
from agent.models.conversation import Conversation


class ExecutionConversation(ExecutionConversationInterface):
    def __init__(self, conversation: Conversation) -> None:
        self._conversation = conversation

    def ask(self, message: str) -> str:
        return ConversationManager().get_answer(
            self._conversation, message, streaming=False, config_type=ConfigType.AGENT_EXECUTION
        )


class MarkExecutionFailedOnErrorTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        execution_id = args[0] if args else kwargs.get("execution_id")
        if execution_id is None:
            return
        try:
            AgentExecution.objects.get(pk=execution_id).mark_failed(
                failure_code=ExecutionFailureCode.RUNTIME_ERROR,
                failure_explanation=f"{type(exc).__name__}: {exc}",
            )
        except AgentExecution.DoesNotExist:
            pass


@shared_task(base=MarkExecutionFailedOnErrorTask, max_retries=0)
def run_agent_execution_task(execution_id: int):
    execution = AgentExecution.objects.select_related("agent", "conversation").get(pk=execution_id)
    execution.mark_in_progress()

    registry = AgentExecutionRegistry()
    execution_cls = registry.get_by_agent_type(execution.agent.agent_type)
    input_data = execution_cls.INPUT_TYPE(**execution.input)

    result = execution_cls().run(input_data, ExecutionConversation(execution.conversation))

    if result.success:
        execution.mark_finished(result.output)
    else:
        execution.mark_failed(
            failure_code=result.failure_code or ExecutionFailureCode.MAX_RETRIES_EXCEEDED,
            failure_explanation=result.failure_summary or "",
        )
