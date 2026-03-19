import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agent", "0025_migrate_re_act_to_tool_calling"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgentExecution",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "agent",
                    models.ForeignKey(
                        help_text="The configured agent this execution runs against.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="executions",
                        to="agent.agent",
                    ),
                ),
                (
                    "execution_key",
                    models.CharField(
                        default="",
                        help_text="EXECUTION_KEY of the execution class used to run this record. Used to resolve the correct class at task time.",
                        max_length=128,
                    ),
                ),
                (
                    "conversation",
                    models.OneToOneField(
                        help_text="Conversation created by the view before the execution task is enqueued.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="agent_execution",
                        to="agent.conversation",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_progress", "In Progress"),
                            ("finished", "Finished"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                (
                    "input",
                    models.JSONField(
                        help_text="Validated input payload matching the execution type's ExecutionInputType schema.",
                    ),
                ),
                (
                    "result",
                    models.JSONField(
                        blank=True,
                        help_text="Structured output from ExecutionResult.output — set when the execution finishes.",
                        null=True,
                    ),
                ),
                (
                    "failure_code",
                    models.CharField(
                        blank=True,
                        help_text="Standardised short error code set when the execution fails.",
                        max_length=128,
                        null=True,
                    ),
                ),
                (
                    "failure_explanation",
                    models.TextField(
                        blank=True,
                        help_text="Human-readable explanation of what went wrong — set when the execution fails.",
                        null=True,
                    ),
                ),
                (
                    "celery_task_id",
                    models.CharField(
                        blank=True,
                        help_text="ID of the Celery task running this execution.",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table_comment": (
                    "Autonomous, programmatic LLM-driven batch jobs. Each record tracks the full "
                    "lifecycle of an agent execution: input, status, result, and timing."
                ),
                "ordering": ["-started_at"],
            },
        ),
    ]
