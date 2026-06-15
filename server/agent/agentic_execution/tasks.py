from celery import Task, shared_task
from enthusiast_common.agentic_execution import ExecutionConversationInterface, ExecutionFailureCode
from enthusiast_common.agentic_execution.memory import ToolScratchpad
from enthusiast_common.agents import ConfigType

from agent.agentic_execution.registry import AgenticExecutionDefinitionRegistry
from agent.conversation import ConversationManager
from agent.models.agentic_execution import AgenticExecution
from agent.models.conversation import Conversation


class ExecutionConversation(ExecutionConversationInterface):
    def __init__(self, conversation: Conversation) -> None:
        self._conversation = conversation
        self._tool_scratchpad = ToolScratchpad()

    def ask(self, message: str) -> str:
        return ConversationManager().get_answer(
            self._conversation,
            message,
            streaming=False,
            config_type=ConfigType.AGENTIC_EXECUTION_DEFINITION,
            tool_scratchpad=self._tool_scratchpad,
        )

    @property
    def tool_scratchpad(self) -> ToolScratchpad:
        """The shared memory that tools write to and validators read from."""
        return self._tool_scratchpad


class MarkExecutionFailedOnErrorTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        execution_id = args[0] if args else kwargs.get("execution_id")
        if execution_id is None:
            return
        try:
            AgenticExecution.objects.get(pk=execution_id).mark_failed(
                failure_code=ExecutionFailureCode.RUNTIME_ERROR,
                failure_explanation=f"{type(exc).__name__}: {exc}",
            )
        except AgenticExecution.DoesNotExist:
            pass


@shared_task(base=MarkExecutionFailedOnErrorTask, max_retries=0)
def run_agentic_execution_task(execution_id: int):
    execution = AgenticExecution.objects.select_related("agent", "conversation").get(pk=execution_id)
    execution.mark_in_progress()

    registry = AgenticExecutionDefinitionRegistry()
    execution_cls = registry.get_by_key(execution.execution_key)
    input_data = execution_cls.INPUT_TYPE(**execution.input)

    result = execution_cls().run(input_data, ExecutionConversation(execution.conversation))

    if result.success:
        execution.mark_finished(result.output)
    else:
        execution.mark_failed(
            failure_code=result.failure_code or ExecutionFailureCode.UNKNOWN,
            failure_explanation=result.failure_summary,
        )
