from django_filters import FilterSet, NumberFilter

from agent.models import Agent


class AgentFilter(FilterSet):
    dataset = NumberFilter(field_name="dataset", required=True)

    class Meta:
        model = Agent
        fields = ["dataset"]
