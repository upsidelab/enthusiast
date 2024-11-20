from django.urls import path

from . import views

urlpatterns = (
    path('api/ask/', views.GetAnswer.as_view(), name='get_answer'),
    path('api/question/<int:id>/feedback/', views.MessageFeedbackView.as_view()),
    path('api/task_status/<str:task_id>/', views.GetTaskStatus.as_view()),
    path("api/conversations/<int:data_set_id>", views.ConversationListView.as_view()),
    path("api/conversation/", views.ConversationCreateView.as_view()),  # Create a new empty conversation.
    path("api/conversation/<int:conversation_id>", views.ConversationRetrieveView.as_view()),  # Get details of an existing conversation.
)
