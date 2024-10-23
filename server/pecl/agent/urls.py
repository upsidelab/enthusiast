from django.urls import path

from . import views

urlpatterns = [
    path('api/ask/', views.GetAnswer.as_view(), name='get_answer'),
    path("api/conversations/<int:data_set_id>", views.ConversationListView.as_view()),
    path('conversation/', views.conversation_view, name='new_conversation'),  # Start a new conversation.
    path('conversation/new/', views.conversation_view, name='new_conversation'),  # Start a new conversation.
    path('conversation/<str:conversation_id>/', views.conversation_view, name='conversation')  # Continue conversation.
]