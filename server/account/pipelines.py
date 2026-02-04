import logging

from django.conf import settings
from social_core.exceptions import AuthForbidden

from utils.functions import import_from_string

logger = logging.getLogger(__name__)


def update_user(strategy, backend, user=None, *args, **kwargs):
    if not user:
        return
    if kwargs.get("is_new") is False:
        return
    try:
        sso_provider_class = import_from_string(settings.SSO_PROVIDER_SERVICE)
        sso_provider_class.update_user(user)
    except NotImplementedError:
        return
    except Exception as e:
        logger.error(e, exc_info=True)
        raise AuthForbidden(backend)
