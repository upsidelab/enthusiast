import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agent", "0028_fix_unique_agent_name_constraint_exclude_deleted"),
    ]

    operations = [
        # Rename the table in-place — no data loss.
        migrations.RenameModel(
            old_name="AgentExecution",
            new_name="AgenticExecution",
        ),
        # Update related_name on the conversation FK (Django state only, no SQL).
        migrations.AlterField(
            model_name="agenticexecution",
            name="conversation",
            field=models.OneToOneField(
                help_text="Conversation created by the view before the execution task is enqueued.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="agentic_execution",
                to="agent.conversation",
            ),
        ),
        # Update help_text to reflect "execution definition" terminology.
        migrations.AlterField(
            model_name="agenticexecution",
            name="execution_key",
            field=models.CharField(
                default="",
                help_text="EXECUTION_KEY of the execution definition class used to run this record. Used to resolve the correct class at task time.",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="agenticexecution",
            name="input",
            field=models.JSONField(
                help_text="Validated input payload matching the execution definition type's ExecutionInputType schema.",
            ),
        ),
        # Update the table comment.
        migrations.AlterModelTableComment(
            name="agenticexecution",
            table_comment="Autonomous, programmatic LLM-driven batch jobs. Each record tracks the full lifecycle of an agentic execution: input, status, result, and timing.",
        ),
    ]