import types
from unittest.mock import patch

import pytest

from .service import ConfigurationService


@pytest.mark.django_db
class TestConfigurationService:
    def test_replace_paths_with_classes_dict_and_list(self):
        service = ConfigurationService()
        data = {
            "a": "builtins.str",
            "b": [{"c": "builtins.list"}],
        }

        result = service._replace_paths_with_classes(data)

        assert result["a"] is str
        assert result["b"][0]["c"] is list

    def test_replace_paths_with_classes_invalid_type(self):
        service = ConfigurationService()
        data = 123

        with pytest.raises(ValueError):
            service._replace_paths_with_classes(data)

    @patch("agent.services.configuration.service.importlib.import_module")
    def test_import_from_string_valid(self, mock_import_module):
        fake_module = types.SimpleNamespace(Foo=int)
        mock_import_module.return_value = fake_module
        service = ConfigurationService()

        result = service._import_from_string("fake_module.Foo")

        assert result is int
        mock_import_module.assert_called_once()

    def test_import_from_string_invalid(self):
        service = ConfigurationService()

        with pytest.raises(ValueError):
            service._import_from_string("not-a-valid-path")
