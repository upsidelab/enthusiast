import importlib
from typing import Any, get_args, get_origin


def import_from_string(path: str):
    module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def extract_type_info(annotation) -> dict:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is list:
        return {"container": "list", "inner_type": extract_type_info(args[0])}

    if origin is dict:
        key_type = args[0].__name__ if args else "Any"
        value_type = args[1].__name__ if args else "Any"
        return {
            "container": "dict",
            "key_type": key_type,
            "value_type": value_type,
        }

    return {"container": None, "inner_type": annotation.__name__}


def get_model_descriptor_from_class_field(class_obj: Any, field_name: str) -> dict:
    model = getattr(class_obj, field_name)
    if model is None:
        return {}
    args = {}
    for field_name, field in model.model_fields.items():
        args[field_name] = {
            "type": extract_type_info(field.annotation),
            "description": field.description,
            "title": field.title or field_name,
        }

    return args

def get_model_descriptor_default_value_from_class(class_obj: Any, field_name: str) -> dict:
    model = getattr(class_obj, field_name)
    if model is None:
        return {}
    args = {}
    for field_name, field in model.model_fields.items():
        args[field_name] = field.default
    return args
