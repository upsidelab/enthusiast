import pytest
from rest_framework.exceptions import ValidationError

from agent.serializers.configuration import (
    AgentConfigSerializer,
    AgentToolConfigSerializer,
    CallbackHandlerConfigSerializer,
    ChatPromptTemplateSerializer,
    EmbeddingsRegistryConfigSerializer,
    LLMConfigSerializer,
    LLMRegistryConfigSerializer,
    LLMToolConfigSerializer,
    ModelsRegistryConfigSerializer,
    PromptTemplateSerializer,
    RegistryConfigSerializer,
    RepositoriesConfigSerializer,
    RetrieverConfigSerializer,
    RetrieversConfigSerializer,
)


class TestRetrieverConfigSerializer:
    def test_valid_data(self):
        data = {"retriever_class": "MyRetriever", "extra_kwargs": {"top_k": "5"}}

        serializer = RetrieverConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["retriever_class"] == "MyRetriever"

    def test_missing_optional(self):
        data = {"retriever_class": "MyRetriever"}

        serializer = RetrieverConfigSerializer(data=data)

        assert serializer.is_valid()
        assert "extra_kwargs" not in serializer.validated_data


class TestRetrieversConfigSerializer:
    def test_valid_data(self):
        data = {
            "document": {"retriever_class": "DocRetriever"},
            "product": {"retriever_class": "ProdRetriever"},
        }

        serializer = RetrieversConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["document"]["retriever_class"] == "DocRetriever"


class TestRepositoriesConfigSerializer:
    def test_valid_data(self):
        data = {
            "user": "UserRepo",
            "message": "MsgRepo",
            "conversation": "ConvRepo",
            "data_set": "DSRepo",
            "document_chunk": "DocChunkRepo",
            "product": "ProdRepo",
            "product_chunk": "ProdChunkRepo",
        }

        serializer = RepositoriesConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["user"] == "UserRepo"


class TestCallbackHandlerConfigSerializer:
    def test_valid_data(self):
        data = {"handler_class": "MyHandler"}

        serializer = CallbackHandlerConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["handler_class"] == "MyHandler"


class TestLLMConfigSerializer:
    def test_valid_data(self):
        data = {
            "llm_class": "MyLLM",
            "callbacks": [{"handler_class": "HandlerA"}, {"handler_class": "HandlerB"}],
        }

        serializer = LLMConfigSerializer(data=data)

        assert serializer.is_valid()
        assert len(serializer.validated_data["callbacks"]) == 2

    def test_missing_optional(self):
        data = {"llm_class": "MyLLM"}

        serializer = LLMConfigSerializer(data=data)

        assert serializer.is_valid()
        assert "callbacks" not in serializer.validated_data


class TestLLMToolConfigSerializer:
    def test_valid_data(self):
        data = {"tool_class": "ToolA", "data_set_id": "123", "llm": "MyLLM"}

        serializer = LLMToolConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["tool_class"] == "ToolA"


class TestAgentToolConfigSerializer:
    def test_valid_data(self):
        data = {"tool_class": "ToolA", "agent": "AgentA"}

        serializer = AgentToolConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["agent"] == "AgentA"


class TestEmbeddingsRegistryConfigSerializer:
    def test_valid_data(self):
        data = {"registry_class": "EmbReg", "providers": {"p1": "Provider1"}}

        serializer = EmbeddingsRegistryConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["registry_class"] == "EmbReg"


class TestLLMRegistryConfigSerializer:
    def test_valid_data(self):
        data = {"registry_class": "LLMReg"}

        serializer = LLMRegistryConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["registry_class"] == "LLMReg"


class TestModelsRegistryConfigSerializer:
    def test_valid_data(self):
        data = {"registry_class": "ModelReg"}

        serializer = ModelsRegistryConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["registry_class"] == "ModelReg"


class TestRegistryConfigSerializer:
    def test_valid_data(self):
        data = {
            "llm": {"registry_class": "LLMReg"},
            "embeddings": {"registry_class": "EmbReg"},
            "model": {"registry_class": "ModelReg"},
        }

        serializer = RegistryConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["llm"]["registry_class"] == "LLMReg"


class TestPromptTemplateSerializer:
    def test_valid_data(self):
        data = {"input_variables": ["a", "b"], "template": "Hello"}

        serializer = PromptTemplateSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["template"] == "Hello"


class TestChatPromptTemplateSerializer:
    def test_valid_data(self):
        data = {"messages": [["system", "Hello"], ["human", "{input}"]]}

        serializer = ChatPromptTemplateSerializer(data=data)

        assert serializer.is_valid()
        assert len(serializer.validated_data["messages"]) == 2

    def test_invalid_role(self):
        data = {"messages": [["invalid", "text"]]}

        serializer = ChatPromptTemplateSerializer(data=data)

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestAgentConfigSerializer:
    def test_valid_with_prompt_template(self):
        data = {
            "agent_class": "MyAgent",
            "llm": {"llm_class": "MyLLM"},
            "repositories": {
                "user": "UserRepo",
                "message": "MsgRepo",
                "conversation": "ConvRepo",
                "data_set": "DSRepo",
                "document_chunk": "DocChunkRepo",
                "product": "ProdRepo",
                "product_chunk": "ProdChunkRepo",
            },
            "retrievers": {
                "document": {"retriever_class": "DocRetriever"},
                "product": {"retriever_class": "ProdRetriever"},
            },
            "injector": "InjectorClass",
            "registry": {
                "llm": {"registry_class": "LLMReg"},
                "embeddings": {"registry_class": "EmbReg"},
                "model": {"registry_class": "ModelReg"},
            },
            "prompt_template": {"input_variables": ["a"], "template": "Hello"},
        }

        serializer = AgentConfigSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["prompt_template"]["template"] == "Hello"

    def test_valid_with_chat_prompt_template(self):
        data = {
            "agent_class": "MyAgent",
            "llm": {"llm_class": "MyLLM"},
            "repositories": {
                "user": "UserRepo",
                "message": "MsgRepo",
                "conversation": "ConvRepo",
                "data_set": "DSRepo",
                "document_chunk": "DocChunkRepo",
                "product": "ProdRepo",
                "product_chunk": "ProdChunkRepo",
            },
            "retrievers": {
                "document": {"retriever_class": "DocRetriever"},
                "product": {"retriever_class": "ProdRetriever"},
            },
            "injector": "InjectorClass",
            "registry": {
                "llm": {"registry_class": "LLMReg"},
                "embeddings": {"registry_class": "EmbReg"},
                "model": {"registry_class": "ModelReg"},
            },
            "chat_prompt_template": {"messages": [["system", "Hello"]]},
        }

        serializer = AgentConfigSerializer(data=data)

        assert serializer.is_valid()
        assert "chat_prompt_template" in serializer.validated_data

    def test_missing_both_prompt_and_chat(self):
        data = {
            "agent_class": "MyAgent",
            "llm": {"llm_class": "MyLLM"},
            "repositories": {
                "user": "UserRepo",
                "message": "MsgRepo",
                "conversation": "ConvRepo",
                "data_set": "DSRepo",
                "document_chunk": "DocChunkRepo",
                "product": "ProdRepo",
                "product_chunk": "ProdChunkRepo",
            },
            "retrievers": {
                "document": {"retriever_class": "DocRetriever"},
                "product": {"retriever_class": "ProdRetriever"},
            },
            "injector": "InjectorClass",
            "registry": {
                "llm": {"registry_class": "LLMReg"},
                "embeddings": {"registry_class": "EmbReg"},
                "model": {"registry_class": "ModelReg"},
            },
        }

        serializer = AgentConfigSerializer(data=data)

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_both_prompt_and_chat_provided(self):
        data = {
            "agent_class": "MyAgent",
            "llm": {"llm_class": "MyLLM"},
            "repositories": {
                "user": "UserRepo",
                "message": "MsgRepo",
                "conversation": "ConvRepo",
                "data_set": "DSRepo",
                "document_chunk": "DocChunkRepo",
                "product": "ProdRepo",
                "product_chunk": "ProdChunkRepo",
            },
            "retrievers": {
                "document": {"retriever_class": "DocRetriever"},
                "product": {"retriever_class": "ProdRetriever"},
            },
            "injector": "InjectorClass",
            "registry": {
                "llm": {"registry_class": "LLMReg"},
                "embeddings": {"registry_class": "EmbReg"},
                "model": {"registry_class": "ModelReg"},
            },
            "prompt_template": {"input_variables": ["a"], "template": "Hello"},
            "chat_prompt_template": {"messages": [["system", "Hello"]]},
        }

        serializer = AgentConfigSerializer(data=data)

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
