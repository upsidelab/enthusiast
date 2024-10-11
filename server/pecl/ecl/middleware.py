import base64

from django.conf import settings
from django.http import HttpResponse

AUTH_TEMPLATE = """

<html> <title>Authentication Required</title> <body> Sorry, you are not authorised to use ECL app. </body> </html>
"""

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _unauthed(self):
        response = HttpResponse(AUTH_TEMPLATE, content_type="text/html")
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response

    def __call__(self, request):
        # Skip /api paths
        if request.path.startswith("/api"):
            return self.get_response(request)

        # Verify basic auth on all other paths
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self._unauthed()
        else:
            authentication = request.META['HTTP_AUTHORIZATION']
        (auth_method, auth) = authentication.split(' ', 1)
        if 'basic' != auth_method.lower():
            return self._unauthed()
        auth = base64.b64decode(auth.strip()).decode('utf-8')
        username, password = auth.split(':', 1)
        if (
            username == settings.BASICAUTH_USERNAME and
            password == settings.BASICAUTH_PASSWORD
        ):
            return self.get_response(request)

        return self._unauthed()
