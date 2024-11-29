# Generated by Django 5.1.1 on 2024-11-29 08:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecl', '0021_delete_documentembedding_and_more'),
    ]

    operations = [
        migrations.AlterModelTableComment(
            name='product',
            table_comment='List of products from a given dataset.',
        ),
        # Improve naming.
        migrations.RenameField(
            model_name='product',
            old_name='company_code',
            new_name='data_set',
        ),
        # Improve constraints - each product should be assigned to a dataset, this field cannot be null.
        migrations.AlterField(
            model_name='product',
            name='data_set',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='ecl.dataset'),
            preserve_default=False,
        ),
    ]
