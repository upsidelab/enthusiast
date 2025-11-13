import json
from typing import Any, Self

from django.core import serializers
from django.db.models import Q
from enthusiast_common.builder import RepositoriesInstances
from enthusiast_common.config import AgentConfig
from enthusiast_common.registry import BaseEmbeddingProviderRegistry
from enthusiast_common.repositories import BaseDataSetRepository, BaseProductRepository
from enthusiast_common.retrievers import BaseProductRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate


class ProductRetriever(BaseProductRetriever):
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

    def find_products_matching_query(self, user_query: str) -> list[Any]:
        search_arguments = self._get_search_query_arguments(user_query)

        filter_arguments = search_arguments.get("filter", None)
        exclude_arguments = search_arguments.get("exclude", None)
        order_by_arguments = search_arguments.get("order_by", None)

        filter_arguments_q = self.build_q(filter_arguments)
        exclude_arguments_q = self.build_q(exclude_arguments)

        return self.product_repo.search_for_data_set_products(
            data_set_id=self.data_set_id,
            filter_arguments=filter_arguments_q,
            exclude_arguments=exclude_arguments_q,
            order_by_arguments=order_by_arguments,
        )[: self.number_of_products]

    def get_sample_products_json(self) -> str:
        sample_products = self.product_repo.filter(data_set_id__exact=self.data_set_id)[: self.max_sample_products]
        return serializers.serialize("json", sample_products)

    def _get_search_query_arguments(self, query: str) -> dict:
        chain = PromptTemplate.from_template(self.prompt_template) | self.llm
        distinct_columns_values = self.product_repo.describe_filtering_columns_for_llm()
        llm_result = chain.invoke(
            {
                "sample_products_json": self.get_sample_products_json(),
                "query": query,
                "distinct_columns_values": distinct_columns_values,
            }
        )
        sanitized_result = llm_result.content.strip("`").removeprefix("json")
        return json.loads(sanitized_result)

    def build_q(self, obj: Any | None) -> Q:
        """
        Convert a nested dict of AND/OR conditions into a Django Q object.
        """
        if not obj:
            return Q()

        q = Q()

        for key, value in obj.items():
            if key == "AND":
                sub_q = Q()
                for item in value:
                    sub_q &= self.build_q(item)
                q &= sub_q
            elif key == "OR":
                sub_q = Q()
                for item in value:
                    sub_q |= self.build_q(item)
                q &= sub_q
            else:
                # fallback for leaf: treat as AND
                q &= Q(**{key: value})

        return q

    @classmethod
    def create(
        cls,
        config: AgentConfig,
        data_set_id: int,
        repositories: RepositoriesInstances,
        embeddings_registry: BaseEmbeddingProviderRegistry,
        llm: BaseLanguageModel,
    ) -> Self:
        return cls(
            data_set_id=data_set_id,
            data_set_repo=repositories.data_set,
            product_repo=repositories.product,
            llm=llm,
            **config.retrievers.product.extra_kwargs,
        )
