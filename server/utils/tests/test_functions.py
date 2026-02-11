import sys
from types import ModuleType
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Field

from utils.functions import (
    get_model_descriptor_from_class_field,
    import_from_string,
)


class SimpleModel(BaseModel):
    name: str = Field(description="A name", title="Name")
    age: int


class DummySimple:
    ARGS_FIELD = SimpleModel


class DummyNoneField:
    ARGS_FIELD = None


dummy_module = ModuleType("dummy_module")
dummy_module.DummySimple = DummySimple
dummy_module.DummyNoneField = DummyNoneField
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


def test_get_model_descriptor_from_class_field_when_model_is_none_returns_empty():
    result = get_model_descriptor_from_class_field(DummyNoneField, "ARGS_FIELD")

    assert result == {}


def test_get_model_descriptor_from_class_field_calls_model_json_schema_and_returns_result():
    with patch.object(SimpleModel, "model_json_schema", return_value={"$defs": {}, "properties": {}}) as mock_schema:
        result = get_model_descriptor_from_class_field(DummySimple, "ARGS_FIELD")

        mock_schema.assert_called_once_with()
        assert result == {"$defs": {}, "properties": {}}
