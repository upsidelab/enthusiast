from django.urls import path

from . import views

urlpatterns = [
    path('api/data_sets', views.DataSetListView.as_view(), name="data_set_list"),
    path('api/data_sets/<int:data_set_id>/users', views.DataSetUserListView.as_view(), name='data_set_user_list'),
    path('api/data_sets/<int:data_set_id>/users/<int:user_id>', views.DataSetUserView.as_view(),
         name='data_set_user_details'),
    path("api/data_sets/<int:data_set_id>/products", views.ProductListView.as_view(), name='data_set_product_list'),
    path("api/data_sets/<int:data_set_id>/documents", views.DocumentListView.as_view(), name='data_set_document_list'),
    path('api/data_sets/<int:data_set_id>/product_sources', views.DataSetProductSourceListView.as_view(), name='data_set_product_source_list'),
    path('api/data_sets/<int:data_set_id>/product_sources/<int:product_source_id>', views.DataSetProductSourceView.as_view(),
         name='data_set_product_source_details'),
    path('api/product_sources/sync',
         views.SyncAllProductSourcesView.as_view(),
         name='all_product_sources_sync'),
    path('api/data_sets/<int:data_set_id>/product_sources/sync',
         views.SyncDataSetProductSourcesView.as_view(),
         name='data_set_product_sources_sync'),
    path('api/data_sets/<int:data_set_id>/product_sources/<int:product_source_id>/sync',
         views.SyncDataSetProductSourceView.as_view(),
         name='data_set_product_source_sync'),
]
