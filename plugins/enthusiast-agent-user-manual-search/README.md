# Enthusiast User Manual Search Agent

The User Manual agent operates over a collection of product manuals and provides precise, context-aware answers to user or support-team questions. Responses include direct citations with links back to the relevant section of the manual, and the agent performs a sanity check to ensure the answer aligns with the documented information before returning it.

## Installing the User Manual Search Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-user-manual-search
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = [
    'enthusiast_agent_user_manual_search.UserManualSearchAgent',
]
```