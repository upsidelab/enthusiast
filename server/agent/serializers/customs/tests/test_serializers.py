import pytest
from rest_framework import serializers
from utils.serializers import ParentDataContextSerializerMixin


class DummyChildSerializer(serializers.Serializer):
    dummy = serializers.CharField()


class DummyListSerializer(serializers.ListSerializer):
    child = DummyChildSerializer()


class DummyTestSerializer(ParentDataContextSerializerMixin, serializers.Serializer):
    context_keys_to_propagate = ["agent_type"]

    child = DummyChildSerializer()
    children = serializers.ListField(child=DummyChildSerializer())
    regular = serializers.CharField()


@pytest.mark.parametrize(
    "initial_context, expected_context",
    [
        ({}, {"agent_type": "abc123"}),
        ({"agent_type": "pre_existing"}, {"agent_type": "pre_existing"}),
    ],
)
def test_context_propagation_from_data(initial_context, expected_context):
    serializer = DummyTestSerializer(context=initial_context.copy())
    data = {
        "agent_type": "abc123",
        "child": {"dummy": "x"},
        "children": [{"dummy": "y"}],
        "regular": "z",
    }

    serializer.is_valid = lambda: True
    serializer.to_internal_value(data)

    assert serializer.context == expected_context


def test_context_propagated_to_nested_serializer_fields():
    serializer = DummyTestSerializer(context={})
    data = {
        "agent_type": "xyz",
        "child": {"dummy": "value"},
        "children": [{"dummy": "val1"}, {"dummy": "val2"}],
        "regular": "something",
    }

    serializer.is_valid = lambda: True
    serializer.to_internal_value(data)

    assert serializer.fields["child"].context["agent_type"] == "xyz"
    assert serializer.fields["children"].child.context["agent_type"] == "xyz"


def test_context_propagated_to_non_serializer_fields():
    class PlainSerializer(ParentDataContextSerializerMixin, serializers.Serializer):
        context_keys_to_propagate = ["agent_type"]

        number = serializers.IntegerField()
        text = serializers.CharField()

    serializer = PlainSerializer(context={})
    data = {"agent_type": "key", "number": 1, "text": "ok"}

    serializer.is_valid = lambda: True
    serializer.to_internal_value(data)

    assert serializer.context["agent_type"] == "key"
    assert serializer.fields["number"].context.get("agent_type") == "key"
    assert serializer.fields["text"].context.get("agent_type") == "key"


def test_no_context_propagation_if_not_in_data():
    serializer = DummyTestSerializer(context={})
    data = {"child": {"dummy": "abc"}, "children": [{"dummy": "x"}], "regular": "text"}

    serializer.is_valid = lambda: True
    serializer.to_internal_value(data)

    assert "agent_type" not in serializer.context
    assert "agent_type" not in serializer.fields["child"].context
    assert "agent_type" not in serializer.fields["children"].child.context
