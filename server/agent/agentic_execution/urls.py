from django.urls import path

from .views import (
    AgenticExecutionDefinitionTypesView,
    AgenticExecutionDetailView,
    AgenticExecutionListView,
    StartAgenticExecutionView,
)

urlpatterns = [
    path("api/agents/<int:agent_id>/agentic-execution-definitions/", AgenticExecutionDefinitionTypesView.as_view(), name="agentic-execution-definitions"),
    path("api/agents/<int:agent_id>/agentic-executions/", StartAgenticExecutionView.as_view(), name="agentic-execution-start"),
    path("api/agentic-executions/", AgenticExecutionListView.as_view(), name="agentic-execution-list"),
    path("api/agentic-executions/<int:pk>/", AgenticExecutionDetailView.as_view(), name="agentic-execution-detail"),
]
