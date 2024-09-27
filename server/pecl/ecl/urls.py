from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/user", views.user_detail),
    path('api/data_sets', views.data_set_list),
    path("api/products/<int:data_set_id>", views.product_list),
    path("api/contents/<int:data_set_id>", views.content_list)
]
