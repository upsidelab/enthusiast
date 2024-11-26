from django.contrib import admin
from .models import EmbeddingModel, EmbeddingDimension, DataSet, Document, DocumentChunkEmbedding

# Register your models here.
admin.site.register(EmbeddingModel)
admin.site.register(EmbeddingDimension)
admin.site.register(DataSet)
admin.site.register(Document)
admin.site.register(DocumentChunkEmbedding)