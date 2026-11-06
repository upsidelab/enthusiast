from django.db import models
from suvereo_common.entities import DomainEntity, EntityField


class Document(DomainEntity, models.Model):
    """A document synced from an external source, indexed for vector search."""

    dataset = models.ForeignKey("catalog.DataSet", on_delete=models.CASCADE, related_name="documents")
    integration = models.ForeignKey(
        "catalog.Integration", on_delete=models.CASCADE, related_name="documents", null=True, blank=True
    )
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    content = models.TextField()

    class Meta:
        db_table_comment = (
            "List of documents being part of a larger data set. A document may be for instance a blog "
            "post. This is the main entity being analysed by ECL engine when user asks questions "
            "regarding company's offer."
        )
        constraints = [models.UniqueConstraint(fields=["dataset", "url"], name="uq_ecommerce_document")]

    class EntityMeta:
        slug = "documents"
        label = "Documents"
        list_fields = [
            EntityField("title"),
            EntityField("url"),
        ]

    def get_indexable_content(self) -> str:
        return f"{self.title}\n{self.content}"

    def __str__(self):
        return self.title
