from typing import Any

from django.conf import settings


def nested_dict_to_list(data: dict[str, Any]) -> Any:
    if isinstance(data, dict) and data and all(not isinstance(v, dict) for v in data.values()):
        return [{"name": k, "path": v} for k, v in data.items()]
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = nested_dict_to_list(value)
        else:
            result[key] = value
    return result


def get_config() -> dict:
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


def merge_settings(base: dict, extend: dict) -> dict:
    result = base.copy()
    for key, value in extend.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_settings(result[key], value)
        else:
            result[key] = value
    return result
