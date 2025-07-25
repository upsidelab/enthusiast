# Generated by Django 5.1.5 on 2025-06-24 12:14

import django.db.models.deletion
import pgvector.django.vector
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_dataset_system_message"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("embedding", pgvector.django.vector.VectorField(null=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="catalog.product"
                    ),
                ),
            ],
        ),
    ]
