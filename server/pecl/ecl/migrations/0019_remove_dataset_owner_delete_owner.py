# Generated by Django 5.1.1 on 2024-11-22 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecl', '0018_dataset_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Owner',
        ),
    ]
