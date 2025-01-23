from django.conf import settings

class ToolRegistry:
    """Registry of tools."""

    def get_plugins(self):
        return settings.AGENT_TOOLS.items()