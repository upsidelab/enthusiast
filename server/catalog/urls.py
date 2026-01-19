from django.urls import path

from . import views

urlpatterns = [
    path("api/sync", views.SyncAllSourcesView.as_view(), name="all_sources_sync"),
    path("api/data_sets", views.DataSetListView.as_view(), name="data_set_list"),
    path("api/data_sets/<int:data_set_id>", views.DataSetDetailView.as_view(), name="data_set_detail"),
    path("api/data_sets/<int:data_set_id>/users", views.DataSetUserListView.as_view(), name="data_set_user_list"),
    path(
        "api/data_sets/<int:data_set_id>/users/<int:user_id>",
        views.DataSetUserView.as_view(),
        name="data_set_user_details",
    ),
    path("api/data_sets/<int:data_set_id>/products", views.ProductListView.as_view(), name="data_set_product_list"),
    path(
        "api/data_sets/<int:data_set_id>/product_sources",
        views.DataSetProductSourceListView.as_view(),
        name="data_set_product_source_list",
    ),
    path(
        "api/data_sets/<int:data_set_id>/product_sources/<int:product_source_id>",
        views.DataSetProductSourceView.as_view(),
        name="data_set_product_source_details",
    ),
    path(
        "api/data_sets/<int:data_set_id>/sync",
        views.SyncDataSetAllSourcesView.as_view(),
        name="data_set_all_sources_sync",
    ),
    path("api/product_sources/sync", views.SyncAllProductSourcesView.as_view(), name="all_product_sources_sync"),
    path(
        "api/data_sets/<int:data_set_id>/product_sources/sync",
        views.SyncDataSetProductSourcesView.as_view(),
        name="data_set_product_sources_sync",
    ),
    path(
        "api/data_sets/<int:data_set_id>/product_sources/<int:product_source_id>/sync",
        views.SyncDataSetProductSourceView.as_view(),
        name="data_set_product_source_sync",
    ),
    path("api/data_sets/<int:data_set_id>/documents", views.DocumentListView.as_view(), name="data_set_document_list"),
    path(
        "api/data_sets/<int:data_set_id>/document_sources",
        views.DataSetDocumentSourceListView.as_view(),
        name="data_set_document_source_list",
    ),
    path(
        "api/data_sets/<int:data_set_id>/document_sources/<int:document_source_id>",
        views.DataSetDocumentSourceView.as_view(),
        name="data_set_document_source_details",
    ),
    path("api/document_sources/sync", views.SyncAllDocumentSourcesView.as_view(), name="all_document_sources_sync"),
    path(
        "api/data_sets/<int:data_set_id>/document_sources/sync",
        views.SyncDataSetDocumentSourcesView.as_view(),
        name="data_set_document_sources_sync",
    ),
    path(
        "api/data_sets/<int:data_set_id>/document_sources/<int:document_source_id>/sync",
        views.SyncDataSetDocumentSourceView.as_view(),
        name="data_set_document_source_sync",
    ),
    path(
        "api/data_sets/<int:data_set_id>/ecommerce_integration",
        views.DataSetECommerceIntegrationView.as_view(),
        name="data_set_ecommerce_integration",
    ),
    path(
        "api/data_sets/<int:data_set_id>/ecommerce_integration/sync",
        views.DataSetECommerceIntegrationSyncView.as_view(),
        name="data_set_ecommerce_integration_sync",
    ),
    path("api/config", views.ConfigView.as_view(), name="config"),
    path(
        "api/config/language_model_providers/<str:provider_name>",
        views.ConfigLanguageModelView.as_view(),
        name="config_language_model_provider",
    ),
    path(
        "api/config/embedding_providers/<str:provider_name>",
        views.ConfigEmbeddingModelView.as_view(),
        name="config_embedding_provider",
    ),
]
