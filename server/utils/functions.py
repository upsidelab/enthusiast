import importlib
from typing import Any

from pydantic_core import PydanticUndefined


def import_from_string(path: str):
    module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_model_descriptor_from_class_field(class_obj: Any, field_name: str) -> dict:
    model = getattr(class_obj, field_name)
    if model is None:
        return {}
    return model.model_json_schema()


def get_model_descriptor_default_value_from_class(class_obj: Any, field_name: str) -> dict:
    model = getattr(class_obj, field_name)
    if model is None:
        return {}
    args = {}
    for field_name, field in model.model_fields.items():
        if field.default is None or field.default is PydanticUndefined:
            continue
        args[field_name] = field.default
    return args
