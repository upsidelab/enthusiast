from django.urls import path

from . import views

urlpatterns = (
    path("api/conversations", views.ConversationListView.as_view()),
    path("api/conversations/agents", views.AvailableAgentsView.as_view()),
    path("api/conversations/<int:conversation_id>", views.ConversationView.as_view()),
    path("api/messages/<int:id>/feedback/", views.MessageFeedbackView.as_view()),
    path("api/task_status/<str:task_id>/", views.GetTaskStatus.as_view()),
    path("api/configuration", views.ConfigView.as_view(), name="configs"),
    path("api/configuration/<int:pk>", views.ConfigDetailsView.as_view(), name="config-details"),
    path("api/configuration/options", views.ConfigOptionsView.as_view(), name="config-options"),
)
