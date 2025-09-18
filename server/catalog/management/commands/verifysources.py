from django.core.management.base import BaseCommand
from pydantic import ValidationError

from catalog.models import DocumentSource, ProductSource
from sync.document.registry import DocumentSourcePluginRegistry
from sync.product.registry import ProductSourcePluginRegistry


class Command(BaseCommand):
    help = "Verify all Product and Document sources to ensure saved config matches plugin implementation"

    def handle(self, *args, **options):
        corrupted_count = 0

        print("Verifying source plugins...")
        models = [(DocumentSource, DocumentSourcePluginRegistry), (ProductSource, ProductSourcePluginRegistry)]
        for model, registry in models:
            source_class_cache = {}
            for source in model.objects.all():
                source_class = source_class_cache.get(source.plugin_name)
                if not source_class:
                    try:
                        source_class = registry().get_plugin_class_by_name(name=source.plugin_name)
                    except Exception:
                        corrupted_count += 1
                        source.corrupted = True
                        source.save(update_fields=["corrupted"])
                        continue
                    source_class_cache[source.plugin_name] = source_class

                try:
                    self._validate_source_config(source_class, source.config)
                    source.corrupted = False
                    source.save(update_fields=["corrupted"])
                except (ValidationError, ValueError):
                    corrupted_count += 1
                    source.corrupted = True
                    source.save(update_fields=["corrupted"])

        print(f"Corrupted sources configurations found: {corrupted_count}")

    @staticmethod
    def _validate_source_config(source_class, config):
        for key, value in config.items():
            class_field_key = key.upper()
            field = getattr(source_class, class_field_key, None)
            if field is not None:
                field(**value)
            if value is not None:
                raise ValueError()
