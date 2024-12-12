from django.db import migrations


class Migration(migrations.Migration):
    sql = """
    ALTER TABLE ecl_dataset RENAME TO catalog_dataset;
    ALTER TABLE ecl_dataset_users RENAME TO catalog_dataset_users;
    ALTER TABLE ecl_document RENAME TO catalog_document;
    ALTER TABLE ecl_documentchunk RENAME TO catalog_documentchunk;
    ALTER TABLE ecl_documentchunkembedding RENAME TO catalog_documentchunkembedding;
    ALTER TABLE ecl_embeddingdimension RENAME TO catalog_embeddingdimension;
    ALTER TABLE ecl_embeddingmodel RENAME TO catalog_embeddingmodel;
    ALTER TABLE ecl_product RENAME TO catalog_product;
    """

    reverse_sql = """
    ALTER TABLE catalog_dataset RENAME TO ecl_dataset;
    ALTER TABLE catalog_dataset_users RENAME TO ecl_dataset_users;
    ALTER TABLE catalog_document RENAME TO ecl_document;
    ALTER TABLE catalog_documentchunk RENAME TO ecl_documentchunk;
    ALTER TABLE catalog_documentchunkembedding RENAME TO ecl_documentchunkembedding;
    ALTER TABLE catalog_embeddingdimension RENAME TO ecl_embeddingdimension;
    ALTER TABLE catalog_embeddingmodel RENAME TO ecl_embeddingmodel;
    ALTER TABLE catalog_product RENAME TO ecl_product;
    """

    dependencies = [
        ('catalog', '0023_alter_product_table_comment_alter_dataset_table_and_more')
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql)
    ]
