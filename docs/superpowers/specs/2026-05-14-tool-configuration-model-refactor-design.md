# Tool Configuration Model Refactor

**Date:** 2026-05-14
**Branch:** feature/ent-283-refactor-tool-configuration-model
**Status:** Approved for implementation

## Problem

Tools in the current system define per-tool configuration via a `CONFIGURATION_ARGS` class variable on `BaseTool`. That configuration is persisted to the DB as a positional array under the `tools` key in the agent's JSON config:

```json
{
  "agent_args": {},
  "prompt_input": {"auto_confirm": true},
  "prompt_extension": {},
  "tools": [{"proxy": ""}, {}]
}
```

At runtime, `BaseAgent.set_runtime_arguments()` injects config into each tool by array index: `self._tools[i].set_runtime_arguments(config["tools"][i])`.

This has two concrete problems:

1. **Positional coupling.** The runtime tool list must match the order of entries in the DB config array. Any tool added to the list after initial configuration (e.g. `StopExecutionTool` appended during agentic execution) has no corresponding config entry → index out of range crash. This is the active bug in PR #386.

2. **Distributed configuration responsibility.** Agent configuration is split across two entities: the agent (agent_args, prompt fields) and its tools (tools array). There is no single place to read the full agent configuration.

## Goal

Make the agent config the sole source of truth. Tools are identified by name in the config, not by position. Tools with no configuration are simply absent from the stored config and silently skipped at runtime.

## Design

### Breaking change

No DB migration. Existing agent configs using the old `tools` array format are incompatible with the new schema. Agents should be re-preconfigured on deploy.

### 1. Data model — `tool_config` named dict

The `tools` positional array is replaced with a `tool_config` dict keyed by the tool's `NAME` string. Only tools that have a non-`None` `CONFIGURATION_ARGS` get an entry.

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

Tools with `CONFIGURATION_ARGS = None` (such as `StopExecutionTool`) have no entry in `tool_config`. Their absence is not an error.

### 2. Runtime loading — `BaseAgent.set_runtime_arguments()`

**File:** `plugins/enthusiast-common/enthusiast_common/agents/base.py`

Replace the positional loop with a named lookup:

```python
def set_runtime_arguments(self, runtime_arguments: Any) -> None:
    tool_config = runtime_arguments.pop("tool_config", {})
    for key, value in runtime_arguments.items():
        class_field_key = key.upper()
        field = getattr(self, class_field_key)
        if field is None:
            continue
        setattr(self, class_field_key, field(**value))
    for tool in self._tools:
        tool_runtime_args = tool_config.get(tool.tool_class.NAME)
        if tool_runtime_args is not None:
            tool.set_runtime_arguments(tool_runtime_args)
```

Key properties:
- `tool_config.get(tool.tool_class.NAME)` — named lookup, order-independent
- Missing entry → skip, no exception. Fixes the `StopExecutionTool` crash.
- `pop("tool_config", {})` default — old configs without the key also won't crash during any transitional period.
- Agent-level arg handling (`agent_args`, `prompt_input`, `prompt_extension`) is unchanged.

### 3. Preconfiguration — `AgentPreconfigurationService`

**File:** `server/agent/services/agent_preconfiguration_service.py`

`_build_default_agent_configuration` builds the initial config when agents are registered. Change the `tools` list to a `tool_config` dict, skipping tools with no `CONFIGURATION_ARGS`:

```python
@staticmethod
def _build_default_agent_configuration(agent_class: BaseAgent):
    return {
        "agent_args": get_model_descriptor_default_value_from_class(agent_class, "AGENT_ARGS"),
        "prompt_input": get_model_descriptor_default_value_from_class(agent_class, "PROMPT_INPUT"),
        "prompt_extension": get_model_descriptor_default_value_from_class(agent_class, "PROMPT_EXTENSION"),
        "tool_config": {
            tool_config.tool_class.NAME: get_model_descriptor_default_value_from_class(
                tool_config.tool_class, "CONFIGURATION_ARGS"
            )
            for tool_config in agent_class.TOOLS
            if tool_config.tool_class.CONFIGURATION_ARGS is not None
        },
    }
```

### 4. Serializer / validation

**File:** `server/agent/serializers/customs/fields.py`

`PydanticModelToolListField` validates the `tools` array on API config updates. Replace it with a dict-based field:

- Rename to `PydanticModelToolConfigField`
- Accepts `{"scrape_product_data": {"proxy": ""}}` instead of `[{"proxy": ""}, {}]`
- Validates each key against the agent's tool list by `NAME`
- Values are validated against the corresponding tool's `CONFIGURATION_ARGS` Pydantic schema
- Keys not present in the agent's tool list → validation error
- Tools with `CONFIGURATION_ARGS = None` are not valid keys

The DRF serializer using this field renames the field from `tools` to `tool_config`. The API contract changes: clients must send `tool_config: {...}` instead of `tools: [...]`.

### 5. Frontend

The React config editor reads and writes the agent `config` JSON. Any component iterating `config.tools` as an array must be updated to iterate `config.tool_config` as an object. The API payload sent on save must use the new key. The specific component needs to be identified during implementation.

## Affected files

| File | Change |
|------|--------|
| `plugins/enthusiast-common/enthusiast_common/agents/base.py` | `set_runtime_arguments` — positional → named lookup |
| `server/agent/services/agent_preconfiguration_service.py` | `_build_default_agent_configuration` — list → dict |
| `server/agent/serializers/customs/fields.py` | `PydanticModelToolListField` → `PydanticModelToolConfigField` |
| `server/agent/serializers/customs/tests/test_fields.py` | Update for dict-based field |
| `server/agent/tests/test_services.py` | Update `EXPECTED_AGENT_CONFIG` shape |
| Frontend config editor component (TBD) | `config.tools[]` → `config.tool_config{}` |

## Out of scope

- No changes to how `CONFIGURATION_ARGS` is declared on tool classes
- No changes to `BaseTool.set_runtime_arguments()` (per-tool injection stays the same)
- No changes to `CatalogEnrichmentConfigProvider` or any `BaseAgentConfigProvider` subclass
- No changes to the `StopExecutionTool` itself
