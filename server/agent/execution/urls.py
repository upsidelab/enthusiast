from django.urls import path

from .views import AgentExecutionDetailView, AgentExecutionListView, StartAgentExecutionView

urlpatterns = [
    path("api/agents/<int:agent_id>/executions/", StartAgentExecutionView.as_view(), name="agent-execution-start"),
    path("api/agent-executions/", AgentExecutionListView.as_view(), name="agent-execution-list"),
    path("api/agent-executions/<int:pk>/", AgentExecutionDetailView.as_view(), name="agent-execution-detail"),
]
