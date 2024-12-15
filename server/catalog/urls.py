from django.urls import path

from . import views

urlpatterns = [
    path('api/data_sets', views.DataSetListView.as_view(), name="data_set_list"),
    path('api/data_sets/<int:data_set_id>/users', views.DataSetUserListView.as_view(), name='data_set_user_list'),
    path('api/data_sets/<int:data_set_id>/users/<int:user_id>', views.DataSetUserView.as_view(),
         name='data_set_user_details'),
    path("api/data_sets/<int:data_set_id>/products", views.ProductListView.as_view(), name='data_set_product_list'),
    path("api/data_sets/<int:data_set_id>/documents", views.DocumentListView.as_view(), name='data_set_document_list'),
]
