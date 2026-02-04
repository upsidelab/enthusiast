from unittest.mock import MagicMock, patch

import pytest
from social_core.exceptions import AuthForbidden

from account.models import User
from account.pipelines import update_user


@pytest.mark.django_db
class TestUpdateUserPipeline:
    def test_returns_early_when_no_user(self):
        strategy = MagicMock()
        backend = MagicMock()
        result = update_user(strategy, backend, user=None)
        assert result is None

    def test_returns_early_when_user_not_new(self):
        from model_bakery import baker

        user = baker.make(User, email="existing@example.com")
        strategy = MagicMock()
        backend = MagicMock()
        result = update_user(strategy, backend, user=user, is_new=False)
        assert result is None

    def test_returns_early_on_not_implemented_error(self):
        from model_bakery import baker

        user = baker.make(User, email="new@example.com")
        strategy = MagicMock()
        backend = MagicMock()
        mock_provider_class = MagicMock()
        mock_provider_class.update_user.side_effect = NotImplementedError
        with patch("account.pipelines.import_from_string", return_value=mock_provider_class):
            result = update_user(strategy, backend, user=user, is_new=True)
        assert result is None
        mock_provider_class.update_user.assert_called_once_with(user)

    def test_raises_auth_forbidden_on_other_exception(self):
        from model_bakery import baker

        user = baker.make(User, email="new@example.com")
        strategy = MagicMock()
        backend = MagicMock()
        mock_provider_class = MagicMock()
        mock_provider_class.update_user.side_effect = ValueError("Update failed")
        with patch("account.pipelines.import_from_string", return_value=mock_provider_class):
            with pytest.raises(AuthForbidden) as exc_info:
                update_user(strategy, backend, user=user, is_new=True)
        assert exc_info.value.backend is backend
        mock_provider_class.update_user.assert_called_once_with(user)
