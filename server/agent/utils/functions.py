from typing import Any


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


def merge_settings(base: dict, extend: dict) -> dict:
    result = base.copy()
    for key, value in extend.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_settings(result[key], value)
        else:
            result[key] = value
    return result
