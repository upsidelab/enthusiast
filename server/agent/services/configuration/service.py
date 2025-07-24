import importlib

from django.conf import settings
from enthusiast_common.config import AgentConfig

from agent.models.agent_config import AgentConfiguration
from agent.utils.functions import nested_dict_to_list


class ConfigurationService:
    def load_config(self, configuration_id):
        configuration = AgentConfiguration.objects.get(pk=configuration_id)
        config = configuration.config
        config_dict = self._replace_paths_with_classes(config)
        return AgentConfig(**config_dict)

    def get_config_options(self) -> dict:
        return {
            "agents": nested_dict_to_list(settings.AVAILABLE_AGENTS),
            "prompt_templates": nested_dict_to_list(settings.AVAILABLE_PROMPT_TEMPLATES),
            "llm": nested_dict_to_list(settings.AVAILABLE_LLM),
            "llm_callback_handlers": nested_dict_to_list(settings.AVAILABLE_LLM_CALLBACK_HANDLERS),
            "agent_callback_handlers": nested_dict_to_list(settings.AVAILABLE_AGENT_CALLBACK_HANDLERS),
            "repositories": nested_dict_to_list(settings.AVAILABLE_REPOSITORIES),
            "retrievers": nested_dict_to_list(settings.AVAILABLE_RETRIEVERS),
            "injectors": nested_dict_to_list(settings.AVAILABLE_INJECTORS),
            "registries": nested_dict_to_list(settings.AVAILABLE_REGISTRIES),
            "tools": nested_dict_to_list(settings.AVAILABLE_TOOLS),
        }

    def _replace_paths_with_classes(self, data):
        if isinstance(data, dict):
            return {k: self._replace_paths_with_classes(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_paths_with_classes(item) for item in data]
        elif isinstance(data, str):
            try:
                return self._import_from_string(data)
            except (ImportError, AttributeError, ValueError):
                return data
        else:
            raise ValueError("Invalid configuration.")

    @staticmethod
    def _import_from_string(path: str):
        module_path, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)


configuration_service = ConfigurationService()
