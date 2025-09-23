from django.urls import path

from . import views

urlpatterns = (
    path("api/conversations", views.ConversationListView.as_view(), name="conversation-list"),
    path("api/conversations/<int:conversation_id>", views.ConversationView.as_view(), name="conversation-details"),
    path(
        "api/conversations/<int:conversation_id>/upload/",
        views.ConversationFileUploadView.as_view(),
        name="conversation-upload",
    ),
    path("api/file-upload-status/<str:task_id>/", views.FileUploadStatusView.as_view(), name="file-upload-status"),
    path("api/supported-file-types/", views.SupportedFileTypesView.as_view(), name="supported-file-types"),
    path("api/messages/<int:id>/feedback/", views.MessageFeedbackView.as_view()),
    path("api/task_status/<str:task_id>/", views.GetTaskStatus.as_view()),
    path("api/agents", views.AgentView.as_view(), name="agents"),
    path("api/agents/<int:pk>", views.AgentDetailsView.as_view(), name="agent-details"),
    path("api/agents/types", views.AgentTypesView.as_view(), name="agent-types"),
)
