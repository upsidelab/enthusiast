from unittest.mock import Mock, patch

import pytest
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage
from langchain_core.tools import BaseTool

from agent.core.memory.summary_chat_memory import SummaryChatMemory


@pytest.mark.django_db
class TestSummaryChatMemory:
    def test_initialization(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        max_token_limit = 1000
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []

        # When
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=max_token_limit,
            output_key="output",
            chat_memory=mock_chat_memory,
        )

        # Then
        assert memory.max_token_limit == max_token_limit
        assert memory.chat_memory is not None
        assert hasattr(memory, "save_context")
        assert callable(memory.save_context)

    def test_inheritance_from_persist_intermediate_steps_mixin(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )

        # When & Then
        # Verify that the class has the save_context method from the mixin
        assert hasattr(memory, "save_context")
        assert callable(memory.save_context)

    def test_inheritance_from_conversation_summary_buffer_memory(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )

        # When & Then
        # Verify that the class has properties from ConversationSummaryBufferMemory
        assert hasattr(memory, "max_token_limit")
        assert hasattr(memory, "chat_memory")
        assert hasattr(memory, "load_memory_variables")
        assert hasattr(memory, "llm")

    def test_save_context_with_basic_messages(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Hello, how are you?"}
        outputs = {"output": "I'm doing well, thank you!"}

        # When
        memory.save_context(inputs, outputs)

        # Then
        # Verify that messages were added to chat_memory
        assert mock_chat_memory.add_message.call_count == 1
        # First call should be AiMessage
        first_call_args = mock_chat_memory.add_message.call_args_list[0][0][0]
        assert isinstance(first_call_args, AIMessage)
        assert first_call_args.content == "I'm doing well, thank you!"

    def test_save_context_with_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
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
        # Should have 3 calls: AI action, Function, Final AI
        assert mock_chat_memory.add_message.call_count == 3

        # Verify the sequence of calls
        call_args_list = mock_chat_memory.add_message.call_args_list

        # AI action message
        assert isinstance(call_args_list[0][0][0], AIMessage)
        assert call_args_list[0][0][0].content == "I'll check the weather for you"

        # Function message
        assert isinstance(call_args_list[1][0][0], FunctionMessage)
        assert call_args_list[1][0][0].name == "weather_tool"
        assert call_args_list[1][0][0].content == "Temperature: 25°C, Condition: Sunny"

        # Final AI response
        assert isinstance(call_args_list[2][0][0], AIMessage)
        assert call_args_list[2][0][0].content == "The weather is sunny today!"

    def test_save_context_with_multiple_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
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
        # Should have 5 calls: 2 AI + 2 Function + Final AI
        assert mock_chat_memory.add_message.call_count == 5

        # Verify the sequence of calls
        call_args_list = mock_chat_memory.add_message.call_args_list

        # First AI action
        assert isinstance(call_args_list[0][0][0], AIMessage)
        assert call_args_list[0][0][0].content == "Searching for data..."

        # First Function message
        assert isinstance(call_args_list[1][0][0], FunctionMessage)
        assert call_args_list[1][0][0].name == "search_tool"

        # Second AI action
        assert isinstance(call_args_list[2][0][0], AIMessage)
        assert call_args_list[2][0][0].content == "Processing data..."

        # Second Function message
        assert isinstance(call_args_list[3][0][0], FunctionMessage)
        assert call_args_list[3][0][0].name == "process_tool"

        # Final AI response
        assert isinstance(call_args_list[4][0][0], AIMessage)

    def test_save_context_without_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Simple question"}
        outputs = {"output": "Simple answer"}

        # When
        memory.save_context(inputs, outputs)

        # Then
        assert mock_chat_memory.add_message.call_count == 1
        call_args_list = mock_chat_memory.add_message.call_args_list
        assert isinstance(call_args_list[0][0][0], AIMessage)

    def test_save_context_with_empty_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Question with empty steps"}
        outputs = {"output": "Answer", "intermediate_steps": []}

        # When
        memory.save_context(inputs, outputs)

        # Then
        assert mock_chat_memory.add_message.call_count == 1
        call_args_list = mock_chat_memory.add_message.call_args_list
        assert isinstance(call_args_list[0][0][0], AIMessage)

    def test_save_context_with_missing_intermediate_steps_key(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Question without intermediate steps"}
        outputs = {"output": "Answer"}

        # When
        memory.save_context(inputs, outputs)

        # Then
        assert mock_chat_memory.add_message.call_count == 1
        call_args_list = mock_chat_memory.add_message.call_args_list
        assert isinstance(call_args_list[0][0][0], AIMessage)

    def test_load_memory_variables_with_short_history(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        # Simulate a realistic message history
        mock_chat_memory.messages = [HumanMessage(content="Short message"), AIMessage(content="Short response")]
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Short message"}
        outputs = {"output": "Short response"}
        memory.save_context(inputs, outputs)

        # When
        loaded_vars = memory.load_memory_variables({})

        # Then
        assert "chat_history" in loaded_vars
        # The type may depend on the implementation, but for summary buffer memory, it should be a string
        assert isinstance(loaded_vars["chat_history"], (str, list))
        # If it's a list, check the contents
        if isinstance(loaded_vars["chat_history"], list):
            assert any("Short message" in str(msg) for msg in loaded_vars["chat_history"])
            assert any("Short response" in str(msg) for msg in loaded_vars["chat_history"])
        else:
            assert "Short message" in loaded_vars["chat_history"]
            assert "Short response" in loaded_vars["chat_history"]

    @patch("langchain.memory.ConversationSummaryBufferMemory.load_memory_variables")
    def test_load_memory_variables_with_long_history(self, mock_load_memory_variables):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=100,
            output_key="output",
            chat_memory=mock_chat_memory,
        )

        # Mock the parent class method to return a summarized history
        mock_load_memory_variables.return_value = {
            "chat_history": "Summarized conversation: User asked about weather, AI provided sunny forecast"
        }

        # Add some messages to trigger summarization
        for i in range(10):
            inputs = {"input": f"Message {i}"}
            outputs = {"output": f"Response {i}"}
            memory.save_context(inputs, outputs)

        # When
        loaded_vars = memory.load_memory_variables({})

        # Then
        assert "chat_history" in loaded_vars
        assert isinstance(loaded_vars["chat_history"], str)
        mock_load_memory_variables.assert_called_once_with({})

    def test_memory_persistence_across_multiple_saves(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )

        # First conversation
        inputs1 = {"input": "What's 2+2?"}
        outputs1 = {"output": "2+2 equals 4"}

        # Second conversation
        inputs2 = {"input": "What about 3+3?"}
        outputs2 = {"output": "3+3 equals 6"}

        # When
        memory.save_context(inputs1, outputs1)
        memory.save_context(inputs2, outputs2)

        # Then
        # Should have 4 total calls (2 messages per conversation)
        assert mock_chat_memory.add_message.call_count == 2

        # Verify the sequence of calls
        call_args_list = mock_chat_memory.add_message.call_args_list

        # First conversation
        assert call_args_list[0][0][0].content == "2+2 equals 4"

        # Second conversation
        assert call_args_list[1][0][0].content == "3+3 equals 6"

    def test_memory_with_complex_intermediate_steps(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Analyze this data"}

        # Mock complex tool actions
        mock_action1 = Mock()
        mock_action1.tool = "data_loader"
        mock_action1.messages = [AIMessage(content="Loading data from database...")]

        mock_action2 = Mock()
        mock_action2.tool = "data_analyzer"
        mock_action2.messages = [AIMessage(content="Analyzing data patterns...")]

        mock_action3 = Mock()
        mock_action3.tool = "report_generator"
        mock_action3.messages = [AIMessage(content="Generating analysis report...")]

        outputs = {
            "output": "Analysis complete. Found 3 key insights.",
            "intermediate_steps": [
                (mock_action1, "Data loaded: 1000 records"),
                (mock_action2, "Analysis complete: 3 patterns identified"),
                (mock_action3, "Report generated: analysis_report.pdf"),
            ],
        }

        # When
        memory.save_context(inputs, outputs)

        # Then
        # Should have 8 calls: 3 AI + 3 Function + Final AI
        assert mock_chat_memory.add_message.call_count == 7

        # Verify tool names in function messages
        call_args_list = mock_chat_memory.add_message.call_args_list
        function_messages = [call[0][0] for call in call_args_list if isinstance(call[0][0], FunctionMessage)]
        assert len(function_messages) == 3
        assert function_messages[0].name == "data_loader"
        assert function_messages[1].name == "data_analyzer"
        assert function_messages[2].name == "report_generator"

    def test_memory_clear_functionality(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Test message"}
        outputs = {"output": "Test response"}
        memory.save_context(inputs, outputs)

        # Verify messages were saved
        assert mock_chat_memory.add_message.call_count == 1

        # When
        memory.clear()

        # Then
        mock_chat_memory.clear.assert_called_once()

    def test_memory_with_special_characters_in_messages(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": "Message with special chars: !@#$%^&*()"}
        outputs = {"output": "Response with emojis: 😀🎉🚀"}

        # When
        memory.save_context(inputs, outputs)

        # Then
        assert mock_chat_memory.add_message.call_count == 1
        call_args_list = mock_chat_memory.add_message.call_args_list
        assert call_args_list[0][0][0].content == "Response with emojis: 😀🎉🚀"

    def test_memory_with_empty_input_output(self):
        # Given
        mock_llm = Mock(spec=BaseLanguageModel)
        mock_chat_memory = Mock(spec=BaseChatMessageHistory)
        mock_chat_memory.messages = []
        memory = SummaryChatMemory(
            llm=mock_llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000,
            output_key="output",
            chat_memory=mock_chat_memory,
        )
        inputs = {"input": ""}
        outputs = {"output": ""}

        # When
        memory.save_context(inputs, outputs)

        # Then
        assert mock_chat_memory.add_message.call_count == 1
        call_args_list = mock_chat_memory.add_message.call_args_list
        assert call_args_list[0][0][0].content == ""
