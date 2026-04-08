from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0027_add_tool_call_id_to_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='conversation_summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='conversation_summary_human_message_count',
            field=models.IntegerField(default=0),
        ),
    ]
