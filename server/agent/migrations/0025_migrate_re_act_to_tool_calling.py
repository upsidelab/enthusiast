from django.db import migrations


def migrate_re_act_to_tool_calling(apps, schema_editor):
    Agent = apps.get_model("agent", "Agent")
    Agent.objects.filter(agent_type="re_act").update(agent_type="tool_calling")


class Migration(migrations.Migration):

    dependencies = [
        ("agent", "0024_alter_agent_description"),
    ]

    operations = [
        migrations.RunPython(migrate_re_act_to_tool_calling, migrations.RunPython.noop),
    ]
