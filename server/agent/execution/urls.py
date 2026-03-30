from django.urls import path

from .views import AgentExecutionDetailView, AgentExecutionListView, AgentExecutionTypesView, StartAgentExecutionView

urlpatterns = [
    path("api/agents/<int:agent_id>/execution-types/", AgentExecutionTypesView.as_view(), name="agent-execution-types"),
    path("api/agents/<int:agent_id>/executions/", StartAgentExecutionView.as_view(), name="agent-execution-start"),
    path("api/agent-executions/", AgentExecutionListView.as_view(), name="agent-execution-list"),
    path("api/agent-executions/<int:pk>/", AgentExecutionDetailView.as_view(), name="agent-execution-detail"),
]
