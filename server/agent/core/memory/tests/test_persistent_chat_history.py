import pytest
from django.contrib.auth import get_user_model
from langchain_core.messages import AIMessage, HumanMessage
from model_bakery import baker

from agent.core.memory.persistent_chat_history import PersistentChatHistory
from agent.core.repositories import DjangoConversationRepository
from agent.models import Agent, Conversation
from catalog.models import DataSet


@pytest.fixture
def conversation():
    user = baker.make(get_user_model())
    data_set = baker.make(DataSet, users=[user])
    agent = baker.make(Agent, dataset=data_set)
    return baker.make(Conversation, user=user, data_set=data_set, agent=agent)


@pytest.mark.django_db
class TestPersistentChatHistory:
    def test_add_message(self, conversation):
        # Given
        conversation_repo = DjangoConversationRepository(Conversation)
        history = PersistentChatHistory(conversation_repo=conversation_repo, conversation_id=conversation.id)
        message = HumanMessage(content="Hello")

        # When
        history.add_message(message)

        # Then
        assert conversation.messages.count() == 1
        stored_message = conversation.messages.first()
        assert stored_message.role == "human"
        assert stored_message.text == "Hello"

    def test_messages_property_order(self, conversation):
        # Given
        conversation_repo = DjangoConversationRepository(Conversation)
        history = PersistentChatHistory(conversation_repo=conversation_repo, conversation_id=conversation.id)
        history.add_message(HumanMessage(content="Message 1"))
        history.add_message(AIMessage(content="Message 2"))

        # When
        messages = history.messages

        # Then
        assert len(messages) == 2
        assert messages[0].content == "Message 1"
        assert isinstance(messages[0], HumanMessage)
        assert messages[1].content == "Message 2"
        assert isinstance(messages[1], AIMessage)

    def test_clear(self, conversation):
        # Given
        conversation_repo = DjangoConversationRepository(Conversation)
        history = PersistentChatHistory(conversation_repo=conversation_repo, conversation_id=conversation.id)
        history.add_message(HumanMessage(content="You will be deleted"))

        # When
        history.clear()

        # Then
        assert conversation.messages.count() == 0
