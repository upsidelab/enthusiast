from typing import Type, Optional

from django.db import models
from langchain_core.callbacks import BaseCallbackHandler
from dataclasses import dataclass, fields
from abc import ABC

from langchain.agents import AgentExecutor
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate

from ..services.conversation import BaseConversationService
from ..llm import BaseLLM, BaseLanguageModelRegistry, BaseDjangoSettingsModelRegistry
from ..repositories.base import (
    BaseUserRepository,
    BaseMessageRepository,
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseRepository,
)
from ..repositories.django import (
    DjangoMessageRepository,
    DjangoConversationRepository,
    DjangoUserRepository,
    DjangoDataSetRepository,
)


class RegistryConfig:
    registry_class: Type[BaseLanguageModelRegistry] = BaseDjangoSettingsModelRegistry
    providers: Optional[dict[str, str]] = None


@dataclass
class LLMConfig:
    model_class: Type[BaseLLM] = BaseLLM
    registry: RegistryConfig = RegistryConfig()
    callbacks: list[BaseCallbackHandler] = None
    streaming: bool = False


@dataclass
class RepositoryConfig:
    model: models.Model
    repo_class: BaseRepository


@dataclass
class RepositoriesConfig:
    user: Type[BaseUserRepository] = DjangoUserRepository
    message: Type[BaseMessageRepository] = DjangoMessageRepository
    conversation: Type[BaseConversationRepository] = DjangoConversationRepository
    data_set: Type[BaseDataSetRepository] = DjangoDataSetRepository


@dataclass
class ModelsConfig:
    user: Type[models.Model]
    message: Type[models.Model]
    conversation: Type[models.Model]
    data_set: Type[models.Model]


@dataclass
class AgentConfig:
    data_set_id: int
    models: ModelsConfig
    prompt_template: str
    llm: LLMConfig = LLMConfig()
    repositories: RepositoriesConfig = RepositoriesConfig()
    # tools:
    # injectors


class AgentBuilder:
    def __init__(self, config: AgentConfig):
        self._config = config

    def build(self):
        repositories = self._build_repositories()
        data_set_repo = getattr(repositories, "data_set", None)
        llm = self._build_llm(data_set_repo)
        prompt = self._build_prompt()
        print(llm, prompt)

    def _build_llm(self, data_set_repo: BaseDataSetRepository) -> BaseLanguageModel:
        llm_registry_class = self._config.llm.registry.registry_class
        if providers := self._config.llm.registry.providers:
            llm_registry = llm_registry_class(providers=providers)
        else:
            llm_registry = llm_registry_class(data_set_repo=data_set_repo)

        llm = self._config.llm.model_class(
            llm_registry=llm_registry,
            callbacks=self._config.llm.callbacks,
            streaming=self._config.llm.streaming,
            data_set_repo=data_set_repo,
        )
        return llm.create(self._config.data_set_id)

    def _build_repositories(self) -> dict[str, BaseRepository]:
        repositories = {}
        repo_fields = fields(self._config.repositories)
        for field in repo_fields:
            name = field.name
            repo_class = getattr(self._config.repositories, name)
            model_class = getattr(self._config.models, name)
            repositories[name] = repo_class(model_class)
        return repositories

    def _build_prompt(self) -> PromptTemplate:
        return PromptTemplate.from_template(self._config.prompt_template)


class Agent(ABC):
    def __init__(
        self,
        data_set_id: int,
    ):
        self._data_set_id = data_set_id

    def create(
        self,
        llm: BaseLLM,
        conversation_service: BaseConversationService,
        callbacks,
        streaming,
        tools,
        injections,
    ) -> AgentExecutor:
        pass
