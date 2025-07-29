import sys
from types import ModuleType
from typing import Dict, List

import pytest
from pydantic import BaseModel, Field

from agent.utils.functions import extract_type_info, get_model_descriptor_from_class_field, import_from_string


class SimpleModel(BaseModel):
    name: str = Field(description="A name", title="Name")
    age: int


class ListModel(BaseModel):
    tags: List[str] = Field(description="List of tags")


class DictModel(BaseModel):
    mapping: Dict[str, int] = Field(title="Mapping field")


class DummySimple:
    ARGS_FIELD = SimpleModel


class DummyList:
    ARGS_FIELD = ListModel


class DummyDict:
    ARGS_FIELD = DictModel


dummy_module = ModuleType("dummy_module")
dummy_module.DummySimple = DummySimple
dummy_module.DummyList = DummyList
dummy_module.DummyDict = DummyDict
sys.modules["dummy_module"] = dummy_module


def test_import_from_string_valid():
    cls = import_from_string("dummy_module.DummySimple")
    assert cls == DummySimple


def test_import_from_string_invalid_module():
    with pytest.raises(ModuleNotFoundError):
        import_from_string("nonexistent.module.Class")


def test_import_from_string_invalid_format():
    with pytest.raises(ValueError):
        import_from_string("invalidformatstring")


def test_import_from_string_invalid_class():
    with pytest.raises(AttributeError):
        import_from_string("dummy_module.MissingClass")


def test_extract_type_info_simple():
    info = extract_type_info(str)

    assert info == {"container": None, "inner_type": "str"}


def test_extract_type_info_list():
    info = extract_type_info(List[str])

    assert info["container"] == "list"
    assert info["inner_type"] == {"container": None, "inner_type": "str"}


def test_extract_type_info_dict():
    info = extract_type_info(Dict[str, int])

    assert info == {"container": "dict", "key_type": "str", "value_type": "int"}


def test_extract_type_info_no_args_dict():
    from typing import Dict as TypingDict

    info = extract_type_info(TypingDict)

    assert info == {"container": "dict", "key_type": "Any", "value_type": "Any"}


def test_get_model_descriptor_from_class_field_simple():
    desc = get_model_descriptor_from_class_field(DummySimple, "ARGS_FIELD")

    assert "name" in desc
    assert desc["name"]["type"] == {"container": None, "inner_type": "str"}
    assert desc["name"]["description"] == "A name"
    assert desc["name"]["title"] == "Name"
    assert "age" in desc
    assert desc["age"]["type"] == {"container": None, "inner_type": "int"}


def test_get_model_descriptor_from_class_field_list():
    desc = get_model_descriptor_from_class_field(DummyList, "ARGS_FIELD")

    assert "tags" in desc
    assert desc["tags"]["type"]["container"] == "list"
    assert desc["tags"]["type"]["inner_type"] == {"container": None, "inner_type": "str"}


def test_get_model_descriptor_from_class_field_dict():
    desc = get_model_descriptor_from_class_field(DummyDict, "ARGS_FIELD")

    assert "mapping" in desc
    assert desc["mapping"]["type"] == {"container": "dict", "key_type": "str", "value_type": "int"}
    assert desc["mapping"]["title"] == "Mapping field"
