from django.db import models
from django.utils import timezone


class AgentExecution(models.Model):
    """Persisted record of a programmatic, autonomous agent execution job.

    Lifecycle: pending → in_progress → finished | failed.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        FINISHED = "finished", "Finished"
        FAILED = "failed", "Failed"

    agent = models.ForeignKey(
        "agent.Agent",
        on_delete=models.PROTECT,
        related_name="executions",
        help_text="The configured agent this execution runs against. Execution type is derived from agent.agent_type.",
    )
    conversation = models.OneToOneField(
        "agent.Conversation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_execution",
        help_text="Conversation created internally by the plugin during run(); populated once the conversation exists.",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    input = models.JSONField(
        help_text="Validated input payload matching the execution type's ExecutionInputType schema.",
    )
    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured output from ExecutionResult.output — set when the execution finishes.",
    )
    failure_code = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="Standardised short error code set when the execution fails.",
    )
    failure_explanation = models.TextField(
        null=True,
        blank=True,
        help_text="Human-readable explanation of what went wrong — set when the execution fails.",
    )
    celery_task_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID of the Celery task running this execution.",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        db_table_comment = (
            "Autonomous, programmatic LLM-driven batch jobs. Each record tracks the full "
            "lifecycle of an agent execution: input, status, result, and timing."
        )

    @property
    def duration_seconds(self) -> float | None:
        """Elapsed time in seconds between start and finish, or None if not yet finished."""
        if self.finished_at is None:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    def mark_in_progress(self) -> None:
        """Transition the record to in_progress."""
        self.status = self.Status.IN_PROGRESS
        self.save(update_fields=["status"])

    def mark_finished(self, result: dict) -> None:
        """Transition the record to finished and persist the execution output.

        Args:
            result: Serializable dict from ExecutionResult.output.
        """
        self.status = self.Status.FINISHED
        self.result = result
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "result", "finished_at"])

    def mark_failed(self, failure_code: str, failure_explanation: str) -> None:
        """Transition the record to failed and persist the error details.

        Args:
            failure_code: Standardised short error code.
            failure_explanation: Human-readable explanation of the failure.
        """
        self.status = self.Status.FAILED
        self.failure_code = failure_code
        self.failure_explanation = failure_explanation
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "failure_code", "failure_explanation", "finished_at"])
