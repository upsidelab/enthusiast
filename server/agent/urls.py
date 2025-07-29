from django.urls import path

from . import views

urlpatterns = (
    path("api/conversations", views.ConversationListView.as_view()),
    path("api/conversations/<int:conversation_id>", views.ConversationView.as_view()),
    path("api/messages/<int:id>/feedback/", views.MessageFeedbackView.as_view()),
    path("api/task_status/<str:task_id>/", views.GetTaskStatus.as_view()),
    path("api/agents", views.AgentView.as_view(), name="agent-create"),
    path("api/agents/<int:pk>", views.AgentDetailsView.as_view(), name="agent-details"),
    path("api/agents/types", views.AgentTypesView.as_view(), name="agent-types"),
    path(
        "api/agents/dataset/<int:pk>",
        views.DatasetAgentView.as_view(),
        name="dataset-agents",
    ),
)
