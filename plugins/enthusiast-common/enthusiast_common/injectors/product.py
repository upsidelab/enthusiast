from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterable

from langchain_core.language_models import BaseLanguageModel

from ..repositories import BaseProductRepository, BaseDataSetRepository

T = TypeVar("T")


class BaseProductRetriever(ABC, Generic[T]):
    def __init__(
        self,
        data_set_id: int,
        data_set_repo: BaseDataSetRepository,
        product_repo: BaseProductRepository,
        llm: BaseLanguageModel,
        prompt_template: str,
        number_of_products: int = 12,
        max_sample_products: int = 12,
    ):
        self.data_set_id = data_set_id
        self.data_set_repo = data_set_repo
        self.product_repo = product_repo
        self.number_of_products = number_of_products
        self.max_sample_products = max_sample_products
        self.prompt_template = prompt_template
        self.llm = llm

    @abstractmethod
    def find_products_matching_query(self, user_query: str) -> Iterable[T]:
        pass
