import pytest
from django.contrib.auth import get_user_model
from langchain_core.messages import AIMessage, HumanMessage

from agent.core.persistent_chat_history import PersistentChatHistory
from agent.models import Conversation
from catalog.models import DataSet


@pytest.mark.django_db
class TestPersistentChatHistory:
    def test_add_message(self):
        # Given
        user = get_user_model().objects.create_user(email="test@example.com")
        data_set = DataSet.objects.create(name="Test DataSet")
        conversation = Conversation.objects.create(user=user, data_set=data_set)
        history = PersistentChatHistory(conversation)
        message = HumanMessage(content="Hello")

        # When
        history.add_message(message)

        # Then
        assert conversation.messages.count() == 1
        stored_message = conversation.messages.first()
        assert stored_message.role == "human"
        assert stored_message.text == "Hello"

    def test_messages_property_order(self):
        # Given
        user = get_user_model().objects.create_user(email="test@example.com")
        data_set = DataSet.objects.create(name="Test DataSet")
        conversation = Conversation.objects.create(user=user, data_set=data_set)
        history = PersistentChatHistory(conversation)
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

    def test_clear(self):
        # Given
        user = get_user_model().objects.create_user(email="test@example.com")
        data_set = DataSet.objects.create(name="Test DataSet")
        conversation = Conversation.objects.create(user=user, data_set=data_set)
        history = PersistentChatHistory(conversation)
        history.add_message(HumanMessage(content="You will be deleted"))

        # When
        history.clear()

        # Then
        assert conversation.messages.count() == 0
