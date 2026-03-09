from django.urls import path

from .views import AgentExecutionDetailView, AgentExecutionListView, AgentExecutionTypeListView

urlpatterns = [
    path("api/agent-executions/types/", AgentExecutionTypeListView.as_view(), name="agent-execution-types"),
    path("api/agent-executions/", AgentExecutionListView.as_view(), name="agent-execution-list"),
    path("api/agent-executions/<int:pk>/", AgentExecutionDetailView.as_view(), name="agent-execution-detail"),
]
