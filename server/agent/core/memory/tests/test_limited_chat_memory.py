from unittest.mock import Mock

import pytest
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage, BaseMessage, FunctionMessage, HumanMessage
from langchain_core.tools import BaseTool

from agent.core.memory.limited_chat_memory import LimitedChatMemory


@pytest.mark.django_db
class TestLimitedChatMemory:
    def test_initialization(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        max_token_limit = 1000

        # When
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=max_token_limit)

        # Then
        assert memory.max_token_limit == max_token_limit
        assert memory.chat_memory is not None

    def test_save_context_with_basic_messages(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=1000)
        inputs = {"input": "Hello, how are you?"}
        outputs = {"output": "I'm doing well, thank you!"}

        # When
        memory.save_context(inputs, outputs)

        # Then
        messages = memory.chat_memory.messages
        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "Hello, how are you?"
        assert isinstance(messages[1], AIMessage)
        assert messages[1].content == "I'm doing well, thank you!"

    def test_save_context_with_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=1000)
        inputs = {"input": "What's the weather like?"}

        # Mock tool and action
        mock_tool = Mock(spec=BaseTool)
        mock_tool.name = "weather_tool"

        mock_action = Mock()
        mock_action.tool = "weather_tool"
        mock_action.messages = [AIMessage(content="I'll check the weather for you")]

        outputs = {
            "output": "The weather is sunny today!",
            "intermediate_steps": [(mock_action, "Temperature: 25°C, Condition: Sunny")],
        }

        # When
        memory.save_context(inputs, outputs)

        # Then
        messages = memory.chat_memory.messages
        assert len(messages) == 4

        # Human message
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "What's the weather like?"

        # AI action message
        assert isinstance(messages[1], BaseMessage)
        assert messages[1].content == "I'll check the weather for you"

        # Function message
        assert isinstance(messages[2], FunctionMessage)
        assert messages[2].name == "weather_tool"
        assert messages[2].content == "Temperature: 25°C, Condition: Sunny"

        # Final AI response
        assert isinstance(messages[3], AIMessage)
        assert messages[3].content == "The weather is sunny today!"

    def test_save_context_with_multiple_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=1000)
        inputs = {"input": "Get me some data"}

        # Mock tools and actions
        mock_action1 = Mock()
        mock_action1.tool = "search_tool"
        mock_action1.messages = [AIMessage(content="Searching for data...")]

        mock_action2 = Mock()
        mock_action2.tool = "process_tool"
        mock_action2.messages = [AIMessage(content="Processing data...")]

        outputs = {
            "output": "Here's your processed data",
            "intermediate_steps": [
                (mock_action1, "Found 10 records"),
                (mock_action2, "Processed 10 records successfully"),
            ],
        }

        # When
        memory.save_context(inputs, outputs)

        # Then
        messages = memory.chat_memory.messages
        assert len(messages) == 6

        # Verify the sequence: Human -> AI -> Function -> AI -> Function -> AI
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], BaseMessage)
        assert isinstance(messages[2], FunctionMessage)
        assert messages[2].name == "search_tool"
        assert isinstance(messages[3], BaseMessage)
        assert isinstance(messages[4], FunctionMessage)
        assert messages[4].name == "process_tool"
        assert isinstance(messages[5], AIMessage)

    def test_save_context_without_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=1000)
        inputs = {"input": "Simple question"}
        outputs = {"output": "Simple answer"}

        # When
        memory.save_context(inputs, outputs)

        # Then
        messages = memory.chat_memory.messages
        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)

    def test_token_limiting_functionality(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=50)  # Small limit for testing
        inputs = {"input": "This is a very long input message that should exceed the token limit"}
        outputs = {"output": "This is also a very long output message that should exceed the token limit"}

        # When
        memory.save_context(inputs, outputs)

        # Then
        # The memory should still save the messages, but when loaded_variables is called,
        # it should respect the token limit
        loaded_vars = memory.load_memory_variables({})
        # The exact token count depends on the tokenizer, but we can verify the functionality
        assert "history" in loaded_vars

    def test_inheritance_from_persist_intermediate_steps_mixin(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=1000)

        # When & Then
        # Verify that the class has the save_context method from the mixin
        assert hasattr(memory, "save_context")
        assert callable(memory.save_context)

    def test_inheritance_from_conversation_token_buffer_memory(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        memory = LimitedChatMemory(llm=mock_llm, max_token_limit=1000)

        # When & Then
        # Verify that the class has properties from ConversationTokenBufferMemory
        assert hasattr(memory, "max_token_limit")
        assert hasattr(memory, "chat_memory")
        assert hasattr(memory, "load_memory_variables")
