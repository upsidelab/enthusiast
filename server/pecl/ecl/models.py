from django.db import models
from openai import OpenAI
from pgvector.django import CosineDistance, VectorField


class Owner(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table_comment = "Owner groups data sets, for instance: all data sets that belong to one company."

class EmbeddingModel(models.Model):
    """ECL Config - list of models to be used."""
    code = models.CharField(max_length=5, null=True)  # Short name - to be displayed on UI
    name = models.CharField(max_length=30, unique=True)  # Full name of a model

    class Meta:
        db_table_comment = "Models used to create embedding vectors. Note: all models from this table will be used when action 'reload all embeddings' is performed by admin."
        db_table = "ecl_embedding_model"


class EmbeddingDimension(models.Model):
    """ECL Config - list of LLM vector lengths to be used for embeddings."""
    dimension = models.IntegerField(unique=True)

    class Meta:
        db_table_comment = "Lengths of embedding vector that are collected from OpenAI for documents or products. For one item we may collect multiple embedding vectors of different lengths. Note: vectors for all dimensions from this table will be collected when action 'reload all embeddings' is performed by admin."
        db_table = "ecl_embedding_dimension"

class DataSet(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(Owner, related_name="data_set", on_delete=models.PROTECT, null=True)

    class Meta:
        db_table_comment = "List of various data sets. One data set may be the whole company's content such as blog posts, or some part of it: a data set may be represent a brand or department."
        db_table = "ecl_data_set"

    def reload_all_embeddings(self):
        """Reloads embeddings for all models and dimensions registered in ECL config.

        Note: this will recalculate only those combinations which are currently defined in ECL config.
        If there are other combinations already stored, those will not be changed. This may happen when
        embeddings for model ALFA and dimensions 216 were calculated before, while now ECL config is set to
        calculate embeddings with model BETA and dimensions set to 1536.
        """
        embedding_models = EmbeddingModel.objects.all()
        embedding_dimensions = EmbeddingDimension.objects.all()

        for m in embedding_models:
            for d in embedding_dimensions:
                self.set_content_embeddings(m, d.dimension)


    def set_content_embeddings(self, model, dimensions):
        """Sets embeddings with a given model and dimension for all the content of the company.

         Embeddings are sourced from OpenAI, args define how we generate embeddings. We would like to
         be able to generate embeddings multiple times for different models and dimensions combinations.

         One content (such as a blog post) may have multiple embeddings calculated. Thanks to this approach
         we are able to precalculate different vectors and flexibly switch between those on admin panel level.

         Args:
             model: EmbeddingModel, ID of an OpenAI model used to generate embeddings.
             dimensions: Integer, length of an embedding vector.
         """
        cnt = 0
        for document in self.document.all():
            cnt += 1
            document.set_embedding(model, dimensions)


class Document(models.Model):
    data_set = models.ForeignKey(DataSet, related_name="document", on_delete=models.PROTECT, null=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    content = models.TextField()

    class Meta:
        db_table_comment = "List of documents being part of a larger data set. A document may be for instance a blog post. This is the main entity being analysed by ECL engine when user asks questions regarding company's offer."

    def set_embedding(self, model, dimensions):
        """Sets embeddings with a given model and dimension for this content.

         For more info please refer to docs on a Company level (parent of this entity).

         Args:
             model: Integer, ID of an OpenAI model used to generate embeddings.
             dimensions: Integer, length of an embedding model.
         """
        # Obtain a new embedding vector for this content.
        client = OpenAI()
        try:
            openai_embedding = client.embeddings.create(model=model.name,
                                                        dimensions=dimensions,
                                                        input=self.content)
            embedding_vector = openai_embedding.data[0].embedding

            # Upsert a new embedding. TODO: prettify upsert method (remove for).
            cnt = 0
            for emb in self.embedding.all().filter(dimensions=dimensions):
                emb.set_embedding(model=model, dimensions=dimensions, embedding_vector=embedding_vector)
                cnt += 1

            if cnt == 0:
                new_emb = DocumentEmbedding(document=self,
                                            model=model,
                                            dimensions=dimensions,
                                            embedding=embedding_vector
                                            )
                new_emb.save()


        except Exception as error:
            pass  #TODO: add error handling (planned along with logging module)


class DocumentEmbedding(models.Model):
    document = models.ForeignKey(Document, related_name="embedding", on_delete=models.PROTECT, null=True)
    model = models.ForeignKey(EmbeddingModel, on_delete=models.PROTECT, null=True)
    dimensions = models.ForeignKey(EmbeddingDimension, on_delete=models.PROTECT, null=True)
    embedding = VectorField()

    class Meta:
        db_table_comment = "Embedding vectors collected for one document. One document may have several different embedding vectors which have different dimensions. Agent processing user's questions chooses the best vector for the purpose."
        db_table = "ecl_document_embedding"

    def set_embedding(self, model, dimensions, embedding_vector):
        """Sets embedding vector for given model and dimensions.

        For more info regarding embedding calculation please refer to docs on a Company level.

        Args:
            model: Integer, ID of an OpenAI model used to generate embeddings.
            dimensions: Integer, length of an embedding model.
            embedding_vector: VectorField, LLM vector with a given dimension.
        """
        self.model = model
        self.dimensions = dimensions
        self.embedding = embedding_vector


class Product(models.Model):
    company_code = models.ForeignKey(DataSet, on_delete=models.PROTECT, null=True)
    entry_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=255)
    properties = models.CharField(max_length=65535)
    categories = models.CharField(max_length=65535)
    price = models.FloatField()

    class Meta:
        db_table_comment = "List of a company's products."

