from datetime import datetime
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from model_bakery import baker

from agent.conversation.manager import ConversationManager
from agent.models import Agent, Conversation, Message
from catalog.models import DataSet


@pytest.mark.django_db
class TestConversationManager:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.manager = ConversationManager()
        self.user = baker.make(get_user_model())
        self.data_set = baker.make(DataSet, users=[self.user])
        self.agent = baker.make(Agent, dataset=self.data_set)

    def test_create_conversation_success(self):
        """Test successful conversation creation."""
        # Given
        user_id = self.user.id

        # When
        conversation = self.manager.create_conversation(user_id=user_id, agent_id=self.agent.id)

        # Then
        assert conversation is not None
        assert conversation.user == self.user
        assert conversation.data_set == self.data_set
        assert conversation.started_at is not None
        assert conversation.summary is None
        assert Conversation.objects.filter(id=conversation.id).exists()

    def test_create_conversation_with_invalid_user_id(self):
        """Test conversation creation with invalid user ID."""
        # Given
        invalid_user_id = 99999

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.create_conversation(user_id=invalid_user_id, agent_id=self.agent.id)

    def test_create_conversation_with_invalid_agent_id(self):
        """Test conversation creation with invalid agent configuration ID."""
        # Given
        user_id = self.user.id
        invalid_agent_id = 99999

        # When & Then
        with pytest.raises(Agent.DoesNotExist):
            self.manager.create_conversation(user_id=user_id, agent_id=invalid_agent_id)

    def test_create_conversation_with_data_set_not_owned_by_user(self):
        """Test conversation creation with data set not owned by user."""
        # Given
        other_user = baker.make(get_user_model())
        other_data_set = baker.make(DataSet, users=[other_user])
        other_agent = baker.make(Agent, dataset=other_data_set)

        # When & Then
        with pytest.raises(Agent.DoesNotExist):
            self.manager.create_conversation(user_id=self.user.id, agent_id=other_agent.id)

    def test_get_conversation_success(self):
        """Test successful conversation retrieval."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        user_id = self.user.id
        data_set_id = self.data_set.id
        conversation_id = conversation.id

        # When
        retrieved_conversation = self.manager.get_conversation(
            user_id=user_id, data_set_id=data_set_id, conversation_id=conversation_id
        )

        # Then
        assert retrieved_conversation == conversation
        assert retrieved_conversation.user == self.user
        assert retrieved_conversation.data_set == self.data_set

    def test_get_conversation_with_invalid_user_id(self):
        """Test conversation retrieval with invalid user ID."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        invalid_user_id = 99999
        data_set_id = self.data_set.id
        conversation_id = conversation.id

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.get_conversation(
                user_id=invalid_user_id, data_set_id=data_set_id, conversation_id=conversation_id
            )

    def test_get_conversation_with_invalid_data_set_id(self):
        """Test conversation retrieval with invalid data set ID."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        user_id = self.user.id
        invalid_data_set_id = 99999
        conversation_id = conversation.id

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.get_conversation(
                user_id=user_id, data_set_id=invalid_data_set_id, conversation_id=conversation_id
            )

    def test_get_conversation_with_invalid_conversation_id(self):
        """Test conversation retrieval with invalid conversation ID."""
        # Given
        user_id = self.user.id
        data_set_id = self.data_set.id
        invalid_conversation_id = 99999

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.get_conversation(
                user_id=user_id, data_set_id=data_set_id, conversation_id=invalid_conversation_id
            )

    def test_get_conversation_with_wrong_user_ownership(self):
        """Test conversation retrieval with conversation owned by different user."""
        # Given
        other_user = get_user_model().objects.create_user(email="other@example.com", password="testpass123")
        other_data_set = DataSet.objects.create(name="Other DataSet")
        other_user.data_sets.add(other_data_set)

        conversation = Conversation.objects.create(
            user=other_user,
            data_set=other_data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        user_id = self.user.id
        data_set_id = self.data_set.id
        conversation_id = conversation.id

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.get_conversation(user_id=user_id, data_set_id=data_set_id, conversation_id=conversation_id)

    @patch("agent.conversation.manager.ConversationManager.get_answer")
    def test_respond_to_user_message_first_message_sets_summary(self, mock_get_answer):
        """Test that first message sets conversation summary."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        user_id = self.user.id
        data_set_id = self.data_set.id
        conversation_id = conversation.id
        message = "Hello, this is my first message"
        streaming = False

        # Mock the get_answer method to create a response message
        mock_get_answer.return_value = None

        # When
        self.manager.respond_to_user_message(
            conversation_id=conversation_id,
            data_set_id=data_set_id,
            user_id=user_id,
            message=message,
            streaming=streaming,
        )

        # Then
        conversation.refresh_from_db()
        assert conversation.summary == message
        mock_get_answer.assert_called_once_with(conversation, message, streaming)

    @patch("agent.conversation.manager.ConversationManager.get_answer")
    def test_respond_to_user_message_subsequent_message_does_not_change_summary(self, mock_get_answer):
        """Test that subsequent messages don't change the conversation summary."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            summary="Original summary",
            agent=self.agent,
        )
        user_id = self.user.id
        data_set_id = self.data_set.id
        conversation_id = conversation.id
        message = "This is a subsequent message"
        streaming = True

        # Mock the get_answer method to create a response message
        mock_get_answer.return_value = None

        # When
        self.manager.respond_to_user_message(
            conversation_id=conversation_id,
            data_set_id=data_set_id,
            user_id=user_id,
            message=message,
            streaming=streaming,
        )

        # Then
        conversation.refresh_from_db()
        assert conversation.summary == "Original summary"
        mock_get_answer.assert_called_once_with(conversation, message, streaming)

    @patch("agent.conversation.manager.ConversationManager.get_answer")
    def test_respond_to_user_message_with_invalid_conversation(self, mock_get_answer):
        """Test responding to message with invalid conversation."""
        # Given
        user_id = self.user.id
        data_set_id = self.data_set.id
        invalid_conversation_id = 99999
        message = "Test message"
        streaming = False

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.respond_to_user_message(
                conversation_id=invalid_conversation_id,
                data_set_id=data_set_id,
                user_id=user_id,
                message=message,
                streaming=streaming,
            )

        # Verify get_answer was not called
        mock_get_answer.assert_not_called()

    def test_record_error_creates_system_message(self):
        """Test that record_error creates a system error message."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        user_message = Message.objects.create(conversation=conversation, role="human", text="User's message")
        user_id = self.user.id
        data_set_id = self.data_set.id
        conversation_id = conversation.id
        error = Exception("Test error message")

        # When
        self.manager.record_error(
            conversation_id=conversation_id, user_id=user_id, data_set_id=data_set_id, error=error
        )

        # Then
        user_message.refresh_from_db()
        assert conversation.messages.count() == 2
        error_message = conversation.messages.last()
        assert error_message.role == "system"
        assert error_message.text == "We couldn't process your request at this time"
        assert error_message.created_at is not None
        assert user_message.answer_failed is True

    def test_record_error_with_invalid_conversation(self):
        """Test record_error with invalid conversation."""
        # Given
        user_id = self.user.id
        data_set_id = self.data_set.id
        invalid_conversation_id = 99999
        error = Exception("Test error message")

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.record_error(
                conversation_id=invalid_conversation_id, user_id=user_id, data_set_id=data_set_id, error=error
            )

    def test_record_error_with_invalid_user(self):
        """Test record_error with invalid user."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        invalid_user_id = 99999
        data_set_id = self.data_set.id
        conversation_id = conversation.id
        error = Exception("Test error message")

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.record_error(
                conversation_id=conversation_id, user_id=invalid_user_id, data_set_id=data_set_id, error=error
            )

    def test_record_error_with_invalid_data_set(self):
        """Test record_error with invalid data set."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        user_id = self.user.id
        invalid_data_set_id = 99999
        conversation_id = conversation.id
        error = Exception("Test error message")

        # When & Then
        with pytest.raises(ObjectDoesNotExist):
            self.manager.record_error(
                conversation_id=conversation_id, user_id=user_id, data_set_id=invalid_data_set_id, error=error
            )

    def test_record_error_with_different_error_types(self):
        """Test record_error with different types of exceptions."""
        # Given
        conversation = Conversation.objects.create(
            user=self.user,
            data_set=self.data_set,
            started_at=datetime.now(),
            agent=self.agent,
        )
        Message.objects.create(conversation=conversation, role="human", text="User's message")
        user_id = self.user.id
        data_set_id = self.data_set.id
        conversation_id = conversation.id

        # Test with different error types
        error_types = [
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            KeyError("Key error"),
            TypeError("Type error"),
        ]

        # When & Then
        for error in error_types:
            self.manager.record_error(
                conversation_id=conversation_id, user_id=user_id, data_set_id=data_set_id, error=error
            )

            # Verify error message was created
            latest_message = conversation.messages.order_by("-created_at").first()
            assert latest_message.role == "system"
            assert latest_message.text == "We couldn't process your request at this time"
