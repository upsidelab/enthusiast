from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from model_bakery import baker

from agent.core.memory.llm_memory_compactor import COMPACTION_INTERVAL, LLMMemoryCompactor
from agent.core.repositories import DjangoConversationRepository
from agent.models import Agent, Conversation
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
def compactor(conversation, llm):
    return LLMMemoryCompactor(
        conversation_repo=DjangoConversationRepository(Conversation),
        conversation_id=conversation.id,
        llm=llm,
    )


@pytest.mark.django_db
class TestLLMMemoryCompactorGetSummary:
    def test_returns_none_when_no_summary_exists(self, compactor):
        assert compactor.get_summary() is None

    def test_returns_stored_summary(self, llm):
        user = baker.make(get_user_model())
        data_set = baker.make(DataSet, users=[user])
        agent = baker.make(Agent, dataset=data_set)
        conversation = baker.make(Conversation, user=user, data_set=data_set, agent=agent, conversation_summary="Existing summary.")

        compactor = LLMMemoryCompactor(
            conversation_repo=DjangoConversationRepository(Conversation),
            conversation_id=conversation.id,
            llm=llm,
        )

        assert compactor.get_summary() == "Existing summary."


@pytest.mark.django_db
class TestLLMMemoryCompactorCompactIfNeeded:
    def _make_messages(self, human_count: int) -> list:
        messages = []
        for _ in range(human_count):
            messages.append(HumanMessage(content="Hello"))
            messages.append(AIMessage(content="Hi there"))
        return messages

    def test_does_not_compact_below_threshold(self, conversation, compactor, llm):
        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL - 1))

        conversation.refresh_from_db()
        assert conversation.conversation_summary is None
        llm.invoke.assert_not_called()

    def test_compacts_at_threshold(self, conversation, compactor, llm):
        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL))

        conversation.refresh_from_db()
        assert conversation.conversation_summary == "This is a summary."
        assert conversation.conversation_summary_human_message_count == COMPACTION_INTERVAL
        llm.invoke.assert_called_once()

    def test_does_not_compact_again_before_next_interval(self, conversation, compactor, llm):
        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL))
        llm.invoke.reset_mock()

        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL + 1))

        llm.invoke.assert_not_called()

    def test_compacts_again_at_next_interval(self, conversation, compactor, llm):
        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL))
        llm.invoke.reset_mock()

        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL * 2))

        conversation.refresh_from_db()
        assert conversation.conversation_summary_human_message_count == COMPACTION_INTERVAL * 2
        llm.invoke.assert_called_once()

    def test_first_compaction_sends_full_history(self, conversation, compactor, llm):
        messages = [HumanMessage(content=f"msg {i}") for i in range(COMPACTION_INTERVAL)]
        messages += [AIMessage(content="response") for _ in range(COMPACTION_INTERVAL)]

        compactor.compact_if_needed(messages)

        call_args = llm.invoke.call_args[0][0]
        assert isinstance(call_args[0], SystemMessage)
        assert isinstance(call_args[1], HumanMessage)
        assert "msg 0" in call_args[1].content
        assert "Existing summary" not in call_args[1].content

    def test_second_compaction_sends_only_new_messages_and_existing_summary(self, conversation, compactor, llm):
        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL))
        llm.invoke.reset_mock()

        compactor.compact_if_needed(self._make_messages(human_count=COMPACTION_INTERVAL * 2))

        call_args = llm.invoke.call_args[0][0]
        assert isinstance(call_args[0], SystemMessage)
        assert "Existing summary" in call_args[1].content
        assert "This is a summary." in call_args[1].content
