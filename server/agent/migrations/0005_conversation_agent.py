# Generated by Django 5.1.5 on 2025-07-01 13:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agent", "0004_auto_20250623_0843"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="agent",
            field=models.CharField(default="Question Answer Agent", max_length=255),
        ),
    ]
