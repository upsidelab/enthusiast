import requests
from enthusiast_common import DocumentDetails, DocumentSourcePlugin
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field


class SanityCMSConfig(RequiredFieldsModel):
    project_id: str = Field(description="Sanity project ID")
    dataset: str = Field(description="Sanity dataset name")
    schema_type: str = Field(description="Sanity schema type to query")
    title_field_name: str = Field(description="Field name for document title")
    content_field_name: str = Field(description="Field name for document content")
    api_key: str = Field(description="Sanity API key", default="")


class SanityCMSDocumentSource(DocumentSourcePlugin):
    CONFIGURATION_ARGS = SanityCMSConfig

    def __init__(self, data_set_id, **kwargs):
        super().__init__(data_set_id)

    def fetch(self) -> list[DocumentDetails]:
        results = []
        offset = 0  # Starting point for product list pagination.
        limit = 100  # Page size.

        base_url = f"https://{self.CONFIGURATION_ARGS.project_id}.api.sanity.io/v1/data/query/{self.CONFIGURATION_ARGS.dataset}"
        headers = (
            {"Authorization": f"Bearer {self.CONFIGURATION_ARGS.api_key}"} if self.CONFIGURATION_ARGS.api_key else {}
        )

        while True:
            query = (
                f'*[_type == "{self.CONFIGURATION_ARGS.schema_type}"] | order(_createdAt asc) '
                f"[{offset}...{offset + limit}] {{"
                f' "content": {self.CONFIGURATION_ARGS.content_field_name},'
                f' "title": {self.CONFIGURATION_ARGS.title_field_name},'
                f' "url": _type + "/" + _id'
                f" }}"
            )
            response = requests.get(base_url, headers=headers, params={"query": query})
            response.raise_for_status()
            data = response.json()

            sanity_posts = data.get("result", [])

            # Loop through each blog post in the response
            for sanity_post in sanity_posts:
                document = self._get_document(sanity_post)
                results.append(document)

            if len(sanity_posts) < limit:
                break

            offset += limit

        return results

    def _get_document(self, sanity_post: dict) -> DocumentDetails:
        title = sanity_post.get(f"{self.CONFIGURATION_ARGS.title_field_name}")
        content_blocks = sanity_post.get(f"{self.CONFIGURATION_ARGS.content_field_name}", [])
        content = self._extract_content(content_blocks)
        url = sanity_post.get("url")
        document = DocumentDetails(url=url, title=title, content=content)
        return document

    @staticmethod
    def _extract_content(content_blocks):
        """
        Converts the Sanity content array into a single string.
        """
        content = []

        for block in content_blocks:
            if block.get("_type") == "block" and "children" in block:
                text = "".join(child.get("text", "") for child in block["children"])
                content.append(text)

        return "\n\n".join(content)
