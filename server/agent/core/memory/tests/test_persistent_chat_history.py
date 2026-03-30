import pytest
from django.contrib.auth import get_user_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from model_bakery import baker

from agent.core.memory.persistent_chat_history import PersistentChatHistory
from agent.core.repositories import DjangoConversationRepository
from agent.models import Agent, Conversation, Message
from catalog.models import DataSet


@pytest.fixture
def conversation():
    user = baker.make(get_user_model())
    data_set = baker.make(DataSet, users=[user])
    agent = baker.make(Agent, dataset=data_set)
    return baker.make(Conversation, user=user, data_set=data_set, agent=agent)


@pytest.mark.django_db
class TestPersistentChatHistory:
    def test_add_human_message(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )

        # When
        history.add_message(HumanMessage(content="Hello"))

        # Then
        assert conversation.messages.count() == 1
        stored = conversation.messages.first()
        assert stored.type == Message.MessageType.HUMAN
        assert stored.text == "Hello"

    def test_add_ai_message(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )

        # When
        history.add_message(AIMessage(content="I can help with that."))

        # Then
        stored = conversation.messages.first()
        assert stored.type == Message.MessageType.AI
        assert stored.text == "I can help with that."

    def test_add_ai_message_with_tool_calls_stored_as_intermediate_step(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )
        message = AIMessage(
            content="",
            tool_calls=[{"id": "call_abc", "name": "search_products", "args": {"query": "shoes"}}],
        )

        # When
        history.add_message(message)

        # Then
        stored = conversation.messages.first()
        assert stored.type == Message.MessageType.INTERMEDIATE_STEP
        assert stored.function_name == "search_products"
        assert stored.tool_call_id == "call_abc"

    def test_add_tool_message_stored_as_function(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )

        # When
        history.add_message(ToolMessage(content="Found 3 products", tool_call_id="call_abc", name="search_products"))

        # Then
        stored = conversation.messages.first()
        assert stored.type == Message.MessageType.FUNCTION
        assert stored.text == "Found 3 products"
        assert stored.function_name == "search_products"
        assert stored.tool_call_id == "call_abc"

    def test_messages_property_basic_order(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )
        history.add_message(HumanMessage(content="Message 1"))
        history.add_message(AIMessage(content="Message 2"))

        # When
        messages = history.messages

        # Then
        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "Message 1"
        assert isinstance(messages[1], AIMessage)
        assert messages[1].content == "Message 2"

    def test_messages_property_reconstructs_tool_call_pair(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )
        synth_id = "call_xyz"
        history.add_message(HumanMessage(content="Find me shoes"))
        history.add_message(AIMessage(
            content="",
            tool_calls=[{"id": synth_id, "name": "search_products", "args": {}}],
        ))
        history.add_message(ToolMessage(
            content="Found 3 shoes",
            tool_call_id=synth_id,
            name="search_products",
        ))
        history.add_message(AIMessage(content="I found 3 shoes for you."))

        # When
        messages = history.messages

        # Then
        assert len(messages) == 4
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert len(messages[1].tool_calls) == 1
        assert messages[1].tool_calls[0]["name"] == "search_products"
        assert isinstance(messages[2], ToolMessage)
        assert messages[2].content == "Found 3 shoes"
        assert messages[2].tool_call_id == messages[1].tool_calls[0]["id"]
        assert isinstance(messages[3], AIMessage)
        assert messages[3].content == "I found 3 shoes for you."

    def test_messages_property_preserves_stored_tool_call_ids(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )
        # Two tool call turns with distinct IDs
        for i in range(2):
            history.add_message(HumanMessage(content=f"Question {i}"))
            history.add_message(AIMessage(
                content="",
                tool_calls=[{"id": f"call_{i}", "name": "search_products", "args": {}}],
            ))
            history.add_message(ToolMessage(content=f"Result {i}", tool_call_id=f"call_{i}", name="search_products"))
            history.add_message(AIMessage(content=f"Answer {i}"))

        # When
        messages = history.messages
        ai_with_tool_calls = [m for m in messages if isinstance(m, AIMessage) and m.tool_calls]
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]

        # Then — stored IDs are round-tripped correctly and paired consistently
        assert len(ai_with_tool_calls) == 2
        assert len(tool_messages) == 2
        assert ai_with_tool_calls[0].tool_calls[0]["id"] == "call_0"
        assert tool_messages[0].tool_call_id == "call_0"
        assert ai_with_tool_calls[1].tool_calls[0]["id"] == "call_1"
        assert tool_messages[1].tool_call_id == "call_1"

    def test_messages_property_excludes_failed_messages(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )
        history.add_message(HumanMessage(content="Will fail"))
        conversation.messages.filter(type=Message.MessageType.HUMAN).update(answer_failed=True)
        history.add_message(HumanMessage(content="Will succeed"))

        # When
        messages = history.messages

        # Then
        assert len(messages) == 1
        assert messages[0].content == "Will succeed"

    def test_clear(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )
        history.add_message(HumanMessage(content="You will be deleted"))

        # When
        history.clear()

        # Then
        assert conversation.messages.count() == 0

    def test_messages_property_handles_system_messages(self, conversation):
        # Given
        history = PersistentChatHistory(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
        )
        history.add_message(SystemMessage(content="An error occurred"))

        # When
        messages = history.messages

        # Then
        assert len(messages) == 1
        assert isinstance(messages[0], SystemMessage)
        assert messages[0].content == "An error occurred"
