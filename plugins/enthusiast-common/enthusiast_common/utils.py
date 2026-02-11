import inspect
import json
from typing import Any, Dict, List, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel, Json, model_validator
from pydantic._internal._model_construction import ModelMetaclass


def prioritize_items(items: list[str], priorities: list[str]):
    items_set = set(items)
    priorities_set = set(priorities)

    result = [p for p in priorities if p in items_set]
    result += [item for item in items if item not in priorities_set]
    return result


def validate_required_vars(cls, name: str, required_vars: dict[str, type]):
    if inspect.isabstract(cls):
        return cls

    for var_name, expected_type in required_vars.items():
        if not hasattr(cls, var_name):
            raise TypeError(f"Class '{name}' must define class variable '{var_name}'")
        value = getattr(cls, var_name)
        if value is None:
            continue

        origin = get_origin(expected_type)

        if origin:
            if isinstance(value, origin):
                continue

        if isinstance(value, expected_type):
            continue

        if isinstance(value, type):
            if issubclass(value, expected_type):
                continue
        raise TypeError(
            f"Class variable '{var_name}' in '{name}' must be of type or subclass of '{expected_type.__name__}', "
            f"but got '{type(value).__name__ if not isinstance(value, type) else value.__name__}'"
        )
    return cls


class RequiredFieldsMeta(ModelMetaclass):
    MAX_DEPTH = 2

    def __new__(cls, name, bases, namespace):
        new_cls = super().__new__(cls, name, bases, namespace)

        annotations = namespace.get("__annotations__", {})
        for field_name, field_type in annotations.items():
            origin = get_origin(field_type)
            args = get_args(field_type)

            if origin is Union:
                if len(args) != 2:
                    raise TypeError(f"Field '{field_name}' in {name} Union must have exactly 2 types, got {len(args)}")

                if type(None) not in args:
                    raise TypeError(f"Field '{field_name}' in {name} Union must include NoneType")

        def check_type_depth(annotation: Any, current_depth=1):
            if current_depth > cls.MAX_DEPTH:
                raise TypeError(f"Exceeded max depth of {cls.MAX_DEPTH} in field annotation")

            origin = get_origin(annotation)
            args = get_args(annotation)

            if origin is None:
                return

            if origin in {list, List, dict, Dict, Union, tuple}:
                for arg in args:
                    check_type_depth(arg, current_depth + 1)

        for field_name, field in getattr(new_cls, "model_fields", {}).items():
            check_type_depth(field.annotation)
        return new_cls


class RequiredFieldsModel(BaseModel, metaclass=RequiredFieldsMeta):
    def __init__(self, **data):
        hints = get_type_hints(self.__class__)
        for field_name, field_type in hints.items():
            if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                if type(None) in field_type.__args__ and field_name not in data:
                    data[field_name] = None
        super().__init__(**data)

    @model_validator(mode="before")
    def convert_json_fields(cls, values: dict) -> dict:
        for name, field in cls.model_fields.items():
            if field.annotation is Json and name in values:
                v = values[name]
                if isinstance(v, dict):
                    values[name] = json.dumps(v)
        return values


class AgentAdditionalArguments(BaseModel):
    AGENT_ARGS: dict[str, str]
    PROMPT_INPUT: dict[str, str]
    PROMPT_EXTENSION: dict[str, str]
    TOOLS: list[dict[str, str]]
