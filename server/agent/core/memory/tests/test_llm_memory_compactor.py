from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from model_bakery import baker

from agent.core.memory.llm_memory_compactor import COMPACTION_INTERVAL, LLMMemoryCompactor
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


@pytest.fixture
def llm():
    mock = MagicMock()
    mock.invoke.return_value = AIMessage(content="This is a summary.")
    return mock


@pytest.fixture
def chat_history():
    return MagicMock(spec=PersistentChatHistory)


@pytest.fixture
def compactor(conversation, llm, chat_history):
    return LLMMemoryCompactor(
        conversation_repo=DjangoConversationRepository(Conversation),
        conversation_id=conversation.id,
        llm=llm,
        chat_history=chat_history,
    )


def _make_langchain_messages(human_count: int) -> list[BaseMessage]:
    messages = []
    for _ in range(human_count):
        messages.append(HumanMessage(content="Hello"))
        messages.append(AIMessage(content="Hi there"))
    return messages


@pytest.mark.django_db
class TestLLMMemoryCompactorGetSummary:
    def test_returns_none_when_no_summary_exists(self, compactor):
        assert compactor.get_summary() is None

    def test_returns_stored_summary(self, llm, chat_history):
        user = baker.make(get_user_model())
        data_set = baker.make(DataSet, users=[user])
        agent = baker.make(Agent, dataset=data_set)
        conversation = baker.make(
            Conversation, user=user, data_set=data_set, agent=agent, conversation_summary="Existing summary."
        )

        compactor = LLMMemoryCompactor(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
            llm=llm,
            chat_history=chat_history,
        )

        assert compactor.get_summary() == "Existing summary."


@pytest.mark.django_db
class TestLLMMemoryCompactorCompactIfNeeded:
    def test_does_not_compact_below_threshold(self, conversation, compactor, llm, chat_history):
        chat_history.messages_after.return_value = _make_langchain_messages(human_count=COMPACTION_INTERVAL - 1)

        compactor.compact_if_needed()

        conversation.refresh_from_db()
        assert conversation.conversation_summary is None
        llm.invoke.assert_not_called()

    def test_compacts_at_threshold(self, conversation, compactor, llm, chat_history):
        db_message = baker.make(Message, conversation=conversation, type=Message.MessageType.HUMAN, text="Hello")
        chat_history.messages_after.return_value = _make_langchain_messages(human_count=COMPACTION_INTERVAL)
        chat_history.last_message_database_id = db_message.id

        compactor.compact_if_needed()

        conversation.refresh_from_db()
        assert conversation.conversation_summary == "This is a summary."
        assert conversation.last_summarized_message_id == db_message.id
        llm.invoke.assert_called_once()

    def test_does_not_compact_again_before_next_interval(self, conversation, compactor, llm, chat_history):
        db_message = baker.make(Message, conversation=conversation, type=Message.MessageType.HUMAN, text="Hello")

        def messages_after_side_effect(message_id):
            if message_id is None:
                return _make_langchain_messages(human_count=COMPACTION_INTERVAL)
            return _make_langchain_messages(human_count=COMPACTION_INTERVAL - 1)

        chat_history.messages_after.side_effect = messages_after_side_effect
        chat_history.last_message_database_id = db_message.id

        compactor.compact_if_needed()
        conversation.refresh_from_db()
        assert conversation.last_summarized_message_id == db_message.id
        llm.invoke.reset_mock()

        compactor.compact_if_needed()

        llm.invoke.assert_not_called()

    def test_compacts_again_at_next_interval(self, conversation, compactor, llm, chat_history):
        db_message_1 = baker.make(Message, conversation=conversation, type=Message.MessageType.HUMAN, text="Hello")
        db_message_2 = baker.make(Message, conversation=conversation, type=Message.MessageType.HUMAN, text="Hello")

        chat_history.messages_after.return_value = _make_langchain_messages(human_count=COMPACTION_INTERVAL)
        chat_history.last_message_database_id = db_message_1.id

        compactor.compact_if_needed()
        llm.invoke.reset_mock()

        chat_history.last_message_database_id = db_message_2.id
        compactor.compact_if_needed()

        conversation.refresh_from_db()
        assert conversation.last_summarized_message_id == db_message_2.id
        llm.invoke.assert_called_once()

    def test_first_compaction_sends_full_history(self, conversation, compactor, llm, chat_history):
        db_message = baker.make(Message, conversation=conversation, type=Message.MessageType.HUMAN, text="Hello")
        messages = [HumanMessage(content=f"msg {i}") for i in range(COMPACTION_INTERVAL)]
        messages += [AIMessage(content="response") for _ in range(COMPACTION_INTERVAL)]
        chat_history.messages_after.return_value = messages
        chat_history.last_message_database_id = db_message.id

        compactor.compact_if_needed()

        call_args = llm.invoke.call_args[0][0]
        assert isinstance(call_args[0], SystemMessage)
        # First message after the prompt should be the first content message, not an existing summary
        assert isinstance(call_args[1], HumanMessage)
        assert "msg 0" in call_args[1].content
        # No "Existing summary:" HumanMessage injected — this is the initial compaction
        assert not any(
            isinstance(m, HumanMessage) and "Existing summary" in m.content
            for m in call_args
        )

    def test_second_compaction_sends_only_new_messages_and_existing_summary(
        self, conversation, compactor, llm, chat_history
    ):
        db_message_1 = baker.make(Message, conversation=conversation, type=Message.MessageType.HUMAN, text="Hello")
        db_message_2 = baker.make(Message, conversation=conversation, type=Message.MessageType.HUMAN, text="Hello")

        chat_history.messages_after.return_value = _make_langchain_messages(human_count=COMPACTION_INTERVAL)
        chat_history.last_message_database_id = db_message_1.id

        compactor.compact_if_needed()
        llm.invoke.reset_mock()

        chat_history.last_message_database_id = db_message_2.id
        compactor.compact_if_needed()

        call_args = llm.invoke.call_args[0][0]
        assert isinstance(call_args[0], SystemMessage)
        assert "Existing summary" in call_args[1].content
        assert "This is a summary." in call_args[1].content
