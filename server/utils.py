from typing import Any, get_args, get_origin


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
