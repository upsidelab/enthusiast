import requests

from enthusiast_common import DocumentSourcePlugin, DocumentDetails


class SanityCMSDocumentSource(DocumentSourcePlugin):
    def __init__(self, data_set_id, config: dict):
        """
        Initialize the plugin with the parameters to access a source system.

        Args:
            data_set_id (int): identifier of a data set that documents are assigned to.
            config (dict): configuration of the plugin
        """
        super().__init__(data_set_id, config)

        # Sanity CMS related parameters.
        self._project_id = config.get('project_id')
        self._dataset = config.get('dataset')
        self._schema_type = config.get('schema_type')
        self._title_field_name = config.get('title_field_name')
        self._content_field_name = config.get('content_field_name')
        self._url = f'https://{self._project_id}.api.sanity.io/v1/data/query/{self._dataset}'

    def fetch(self) -> list[DocumentDetails]:
        results = []
        query = f'*[_type == "{self._schema_type}"] {{ {self._title_field_name}, {self._content_field_name}, "url": _type + "/" + _id }}'
        response = requests.get(self._url, params={'query': query})
        response.raise_for_status()
        data = response.json()

        # Loop through each blog post in the response
        for sanity_post in data.get("result", []):
            document = self._get_document(sanity_post)
            results.append(document)

        return results

    def _get_document(self, sanity_post: dict) -> DocumentDetails:
        title = sanity_post.get(f'{self._title_field_name}')
        content_blocks = sanity_post.get(f'{self._content_field_name}', [])
        content = self._extract_content(content_blocks)
        url = sanity_post.get('url')
        document = DocumentDetails(
            url=url,
            title=title,
            content=content
        )
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