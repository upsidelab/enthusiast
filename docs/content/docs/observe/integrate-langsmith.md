---
sidebar_position: 1
---

# Integrate LangSmith

[LangSmith](https://www.langchain.com/langsmith) is a developer platform that helps teams manage LLM-powered application lifecycle. 
It comes out of the box with LangChain, which Enthusiast uses internally. 

To enable LangSmith integration, add the following environment variables when running the worker process:

```shell
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<API_KEY>
```

When you start the worker, it will automatically send execution traces to LangSmith, allowing your team to get visibility into the LLM Operations. 

[Read more about LangSmith](https://www.langchain.com/langsmith)
