from django.contrib import admin
from .models import EmbeddingModels, EmbeddingDimensions, Companies, Contents, ContentEmbeddings, Question, Conversation

# Register your models here.
admin.site.register(EmbeddingModels)
admin.site.register(EmbeddingDimensions)
admin.site.register(Companies)
admin.site.register(Contents)
admin.site.register(ContentEmbeddings)