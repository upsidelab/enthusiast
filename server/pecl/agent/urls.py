from django.urls import path

from . import views

urlpatterns = (
    path('api/question/<int:id>/feedback/', views.MessageFeedbackView.as_view()),
    path('api/task_status/<str:task_id>/', views.GetTaskStatus.as_view()),
    path("api/conversations/<int:data_set_id>", views.ConversationListView.as_view()),
    path("api/conversation/", views.ConversationCreateView.as_view()),
    path("api/conversation/<int:conversation_id>", views.ConversationRetrieveView.as_view()),
)
