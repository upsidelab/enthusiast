# Enthusiast Competitor Research Agent

The Competitor Research agent extracts attributes from web pages. It can be customized to pull different attribute sets and can flag unclear or missing information, triggering a human-in-the-loop step when clarification is required.

## Installing the Competitor Research Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-competitor-research
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = [
    "enthusiast_agent_competitor_research.CompetitorResearchAgent"
]
```