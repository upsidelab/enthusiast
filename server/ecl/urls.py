from django.urls import path

from . import views

urlpatterns = [
    path('api/data_sets', views.DataSetListView.as_view()),
    path("api/products/<int:data_set_id>/", views.ProductListView.as_view(), name='product_list'),
    path("api/documents/<int:data_set_id>/", views.DocumentListView.as_view(), name='document_list'),
    path('embedding/', views.embedding_view, name='embedding'),
]
