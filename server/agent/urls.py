from django.urls import path

from . import views

urlpatterns = (
    path("api/conversations", views.ConversationListView.as_view()),
    path("api/conversations/<int:conversation_id>", views.ConversationView.as_view()),
    path("api/messages/<int:id>/feedback/", views.MessageFeedbackView.as_view()),
    path("api/task_status/<str:task_id>/", views.GetTaskStatus.as_view()),
    path("api/agents", views.AvailableAgentsView.as_view(), name="available-agents"),
    path("api/agents/configuration", views.ConfigView.as_view(), name="configs"),
    path(
        "api/agents/configuration/dataset/<int:pk>",
        views.DatasetConfigView.as_view(),
        name="dataset-configs",
    ),
    path("api/agents/configuration/<int:pk>", views.ConfigDetailsView.as_view(), name="config-details"),
)
