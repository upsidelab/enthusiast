# Generated by Django 5.1.1 on 2024-10-04 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecl', '0009_rename_embeddingdimensions_embeddingdimension_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='company',
            new_name='data_set'
        ),
        migrations.RenameField(
            model_name='documentembedding',
            old_name='content',
            new_name='document'
        ),
    ]
