import requests
from enthusiast_vertical_common.interfaces import DocumentSourcePlugin
from enthusiast_vertical_common.structures import DocumentDetails
from pydantic import Field
from suvereo_common.utils import RequiredFieldsModel


class SanityCMSConfig(RequiredFieldsModel):
    project_id: str = Field(title="Project ID", description="Sanity project ID")
    dataset: str = Field(title="Dataset name", description="Sanity dataset name")
    schema_type: str = Field(title="Schema type", description="Sanity schema type to query")
    title_field_name: str = Field(title="Title field name", description="Field name for document title")
    content_field_name: str = Field(title="Content field name", description="Field name for document content")
    api_key: str = Field(title="API key", description="Sanity API key", default="")


class SanityCMSDocumentSource(DocumentSourcePlugin):
    TYPE = "sanity-cms"
    NAME = "Sanity CMS"
    CONFIGURATION_ARGS = SanityCMSConfig

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
        title = sanity_post.get("title")
        content = self._extract_content(sanity_post.get("content"))
        url = sanity_post.get("url")
        document = DocumentDetails(url=url, title=title, content=content)
        return document

    @staticmethod
    def _extract_content(content) -> str:
        """Flatten a Sanity content value into a string.

        Handles Portable Text (a list of blocks) and falls back to the raw value
        for plain-text fields.
        """
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return str(content)

        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("_type") == "block" and "children" in block:
                parts.append("".join(child.get("text", "") for child in block["children"]))
        return "\n\n".join(parts)
