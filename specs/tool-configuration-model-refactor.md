# Tool Configuration Model Refactor

## Summary

Replaced the positional `tools: [{...}, {}]` array in agent DB configs with a named `tool_config: {"tool_name": {...}}` dict. This fixes a crash in agentic execution and removes positional coupling between the runtime tool list and stored configuration.

---

## Problem

Tools in the system define per-tool configuration via `CONFIGURATION_ARGS` on `BaseTool`. That configuration was persisted as a positional array under the `tools` key in the agent's JSON config:

```json
{
  "agent_args": {},
  "prompt_input": {"auto_confirm": true},
  "prompt_extension": {},
  "tools": [{"proxy": ""}, {}]
}
```

At runtime, `BaseAgent.set_runtime_arguments()` injected config into each tool by array index: `self._tools[i].set_runtime_arguments(config["tools"][i])`.

Two concrete problems:

1. **Positional coupling.** `StopExecutionTool` is appended to the tool list during agentic execution at runtime. The DB config was created with N tools; at runtime there are N+1. The index access for the last tool raised `IndexError` — all agentic executions crashed on initialisation.

2. **Distributed config responsibility.** Agent configuration was split across the agent (agent_args, prompt fields) and its tools (tools array). No single place held the full config.

---

## Solution

`tool_config` is a dict keyed by `tool.NAME`. Tools with no `CONFIGURATION_ARGS` have no entry. A missing entry is silently skipped — not an error.

```json
{
  "agent_args": {},
  "prompt_input": {"auto_confirm": true},
  "prompt_extension": {},
  "tool_config": {
    "scrape_product_data": {"proxy": ""}
  }
}
```

---

## Backend Changes

### `BaseAgent.set_runtime_arguments` (`enthusiast-common`)

Named lookup replaces the positional index loop:

```python
def set_runtime_arguments(self, runtime_arguments: Any) -> None:
    tool_config = runtime_arguments.get("tool_config", {})
    for key, value in runtime_arguments.items():
        if key == "tool_config":
            continue
        # ... agent-level field injection unchanged ...
    for tool in self._tools:
        tool_runtime_args = tool_config.get(tool.NAME)
        if tool_runtime_args is not None:
            tool.set_runtime_arguments(tool_runtime_args)
```

Tools absent from `tool_config` are skipped without raising. This fixes the `StopExecutionTool` crash.

### `AgentPreconfigurationService._build_default_agent_configuration`

Builds a `tool_config` dict instead of a `tools` list. Tools with `CONFIGURATION_ARGS = None` are excluded:

```python
"tool_config": {
    tool_config.tool_class.NAME: get_model_descriptor_default_value_from_class(
        tool_config.tool_class, "CONFIGURATION_ARGS"
    )
    for tool_config in agent_class.TOOLS
    if tool_config.tool_class.CONFIGURATION_ARGS is not None
},
```

### `PydanticModelToolConfigField` (new, replaces `PydanticModelToolListField`)

Validates the `tool_config` dict on API config updates:

- Accepts `{"scrape_product_data": {"proxy": ""}}` instead of `[{"proxy": ""}, {}]`
- Validates each key against the agent's tool list by `NAME`
- Validates values against the tool's `CONFIGURATION_ARGS` Pydantic schema
- Unknown tool names → validation error `"Unknown tool: {name}"`
- Tools with `CONFIGURATION_ARGS = None` are not valid keys

`AgentConfigSerializer` and `AgentChoiceSerializer` were updated to use `tool_config`. `AgentTypesView` builds the `tool_config` dict filtered by `CONFIGURATION_ARGS is not None`.

### `verifyagents` Management Command

Updated to validate tools by named lookup via `tool_config_entry.tool_class.NAME` instead of positional index. Missing keys in `tool_config` mark the agent as corrupted. Non-dict config values (`TypeError`) are also caught.

---

## Frontend Changes

`AgentConfig.tool_config` and `AgentChoice.tool_config` replace the old `tools` array in the TypeScript types.

The form flattens the two-level structure to `tool_config_${toolName}_${fieldName}` flat keys for React Hook Form state, then reconstructs the nested dict on submit. Server-side validation errors are mapped back to the same flat keys for inline field highlighting. The config form renders each tool group in its own labelled bordered card.

---

## Breaking Change

No DB migration. Existing agent configs with the old `tools: [...]` format are incompatible. **Agents must be re-preconfigured on deploy.**
