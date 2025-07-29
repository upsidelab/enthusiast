import inspect
from typing import Any, Dict, List, Union, get_args, get_origin

from pydantic import BaseModel
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
        for field_name, field in getattr(new_cls, "model_fields", {}).items():
            origin = get_origin(field.annotation)
            if origin is Union:
                raise TypeError(f"Union/Optional type not allowed for field '{field_name}' in {name}")

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
    pass


class AgentAdditionalArguments(BaseModel):
    AGENT_ARGS: dict[str, str]
    PROMPT_INPUT: dict[str, str]
    PROMPT_EXTENSION: dict[str, str]
    TOOLS: list[dict[str, str]]
