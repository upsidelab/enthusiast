import os

from django.http import HttpResponseForbidden


class PreviewTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.preview_api_token = os.environ.get("ECL_PREVIEW_API_TOKEN")

    def __call__(self, request):
        authorization_header = request.headers.get("Authorization", "")
        if request.path.startswith("/api") and authorization_header != f"Bearer {self.preview_api_token}":
            return HttpResponseForbidden()

        response = self.get_response(request)
        return response
