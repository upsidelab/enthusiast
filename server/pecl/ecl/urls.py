from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/user", views.user_detail),
    path('api/data_sets', views.data_set_list),
    path("api/products/<int:data_set_id>", views.product_list),
    path("api/contents/<int:data_set_id>", views.document_list),
    path('api/ask/', views.GetAnswer.as_view(), name='get_answer'),
    path('conversation/', views.conversation_view, name='new_conversation'),  # Start a new conversation.
    path('conversation/new/', views.conversation_view, name='new_conversation'),  # Start a new conversation.
    path('conversation/<str:conversation_id>/', views.conversation_view, name='conversation'),  # Continue conversation.
    path('embedding/', views.embedding_view, name='embedding'),
]
