from django.urls import path

from . import views

urlpatterns = [
    path("api/plugins/document_source_plugins", views.GetDocumentSourcePlugins.as_view()),
    path("api/plugins/product_source_plugins", views.GetProductSourcePlugins.as_view()),
    path("api/plugins/ecommerce_integration_plugins", views.GetECommerceIntegrationPlugins.as_view()),
]
