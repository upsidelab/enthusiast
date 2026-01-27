import logging

from django.conf import settings
from enthusiast_common.agents import BaseAgent
from utils.functions import get_model_descriptor_default_value_from_class

from agent.core.registries.agents.agent_registry import AgentRegistry
from agent.models import Agent
from agent.serializers.configuration import AgentSerializer
from catalog.models import DataSet

logger = logging.getLogger("AgentService")


class AgentService:
    @staticmethod
    def preconfigure_available_agents(data_set: DataSet):
        registry = AgentService._get_registry()

        for agent_type, agent_details in settings.AVAILABLE_AGENTS.items():
            if Agent.all_objects.filter(dataset=data_set, agent_type=agent_type).exists():
                continue

            agent_class = registry.get_agent_class_by_type(agent_type=agent_type)
            data = {
                "name": agent_details["name"],
                "description": agent_details.get("description", ""),
                "config": AgentService._build_default_agent_configuration(agent_class),
                "dataset": data_set.pk,
                "agent_type": agent_type,
            }
            agent_serializer = AgentSerializer(data=data)
            if not agent_serializer.is_valid():
                logger.warning(f"Cannot configure {agent_type}, reason: {agent_serializer.errors}")
                continue

            agent_serializer.save()

    @staticmethod
    def _get_registry():
        return AgentRegistry()

    @staticmethod
    def _build_default_agent_configuration(agent_class: BaseAgent):
        return {
            "agent_args": get_model_descriptor_default_value_from_class(agent_class, "AGENT_ARGS"),
            "prompt_input": get_model_descriptor_default_value_from_class(agent_class, "PROMPT_INPUT"),
            "prompt_extension": get_model_descriptor_default_value_from_class(agent_class, "PROMPT_EXTENSION"),
            "tools": [
                get_model_descriptor_default_value_from_class(tool_config.tool_class, "CONFIGURATION_ARGS")
                for tool_config in agent_class.TOOLS
            ],
        }
