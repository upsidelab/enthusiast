from django.urls import path

from . import views

urlpatterns = [
    path("api/plugins/document_source_plugins", views.GetDocumentSourcePlugins.as_view()),
    path("api/plugins/product_source_plugins", views.GetProductSourcePlugins.as_view()),
]
