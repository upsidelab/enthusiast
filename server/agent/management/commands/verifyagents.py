from copy import deepcopy

from django.core.management.base import BaseCommand
from pydantic import ValidationError

from agent.core.registries.agents.agent_registry import AgentRegistry, AgentRegistryError
from agent.models import Agent


class Command(BaseCommand):
    help = "Verify all Agent instances to ensure saved config matches agent implementation"

    def handle(self, *args, **options):
        agent_types_cache = {}
        corrupted_count = 0

        print("Verifying agents...")

        for agent in Agent.objects.all():
            agent_class = agent_types_cache.get(agent.agent_type)

            if not agent_class:
                try:
                    agent_class = AgentRegistry().get_agent_class_by_type(agent_type=agent.agent_type)
                except AgentRegistryError:
                    corrupted_count += 1
                    agent.corrupted = True
                    agent.save(update_fields=["corrupted"])
                    continue
                agent_types_cache[agent.agent_type] = agent_class

            config = deepcopy(agent.config)
            tools_config = config.pop("tools", [])

            try:
                self._validate_agent_config(agent_class, config, tools_config)
            except (ValidationError, IndexError):
                corrupted_count += 1
                agent.corrupted = True
                agent.save(update_fields=["corrupted"])

        print(f"Corrupted agent configurations found: {corrupted_count}")

    @staticmethod
    def _validate_agent_config(agent_class, config, tools_config):
        for key, value in config.items():
            class_field_key = key.upper()
            field = getattr(agent_class, class_field_key, None)
            if field is None:
                continue
            field(**value)

        if len(agent_class.TOOLS) != len(tools_config):
            raise ValidationError.from_exception_data("Agent configurations do not match", line_errors=[])

        for index, tool in enumerate(agent_class.TOOLS):
            field = getattr(tool, "CONFIGURATION_ARGS", None)
            if field is None:
                continue
            field(**tools_config[index])
