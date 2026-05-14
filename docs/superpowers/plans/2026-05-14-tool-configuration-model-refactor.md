# Tool Configuration Model Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the positional `tools` array in agent DB configs with a named `tool_config` dict keyed by `tool.NAME`, eliminating positional coupling and the agentic execution crash caused by dynamically-added tools.

**Architecture:** `BaseAgent.set_runtime_arguments` switches from index-based to name-based tool lookup. The preconfiguration service builds a dict instead of a list. The DRF serializer field validates a dict instead of a list. The frontend flattens/reconstructs the two-level `tool_config` structure using `tool_config_${toolName}_${fieldName}` key patterns.

**Tech Stack:** Python 3.12, Django 5, DRF, Pydantic v2, React 18, TypeScript 5.8

**Spec:** `docs/superpowers/specs/2026-05-14-tool-configuration-model-refactor-design.md`

---

## File Map

| File | Change |
|------|--------|
| `plugins/enthusiast-common/enthusiast_common/agents/base.py` | `set_runtime_arguments` named lookup |
| `server/agent/tests/test_runtime_arguments.py` | **New** — unit tests for named lookup |
| `server/agent/services/agent_preconfiguration_service.py` | Build `tool_config` dict |
| `server/agent/tests/test_services.py` | Update expected config shape |
| `server/agent/serializers/customs/fields.py` | New `PydanticModelToolConfigField` |
| `server/agent/serializers/customs/tests/test_fields.py` | Update field tests |
| `server/agent/serializers/configuration.py` | Update `AgentChoiceSerializer` + `AgentConfigSerializer` |
| `server/agent/views.py` | Build `tool_config` dict in available agents endpoint |
| `frontend/src/lib/types.ts` | `AgentConfig.tools` → `tool_config` |
| `frontend/src/lib/api/agents.ts` | `AgentChoice.tools` → `tool_config` |
| `frontend/src/lib/form-utils.ts` | Handle 2-level nesting in flatten |
| `frontend/src/components/agents-table/hooks/use-agent-form.ts` | Build/parse tool_config |
| `frontend/src/components/agents-table/agent-configuration-form.tsx` | Render tool_config dict |

---

## Task 1: Update `BaseAgent.set_runtime_arguments` — named lookup

**Files:**
- Modify: `plugins/enthusiast-common/enthusiast_common/agents/base.py:69-78`
- Create: `server/agent/tests/test_runtime_arguments.py`

---

- [ ] **Step 1.1: Write failing tests**

Create `server/agent/tests/test_runtime_arguments.py`:

```python
from unittest.mock import MagicMock
from enthusiast_common.agents.base import BaseAgent


class _StubAgent:
    """Minimal agent-like object for testing set_runtime_arguments without metaclass validation."""
    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None

    def __init__(self, tools):
        self._tools = tools


def test_set_runtime_arguments_injects_config_by_tool_name():
    tool = MagicMock()
    tool.NAME = "my_tool"
    agent = _StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {"my_tool": {"proxy": "http://example.com"}},
    })

    tool.set_runtime_arguments.assert_called_once_with({"proxy": "http://example.com"})


def test_set_runtime_arguments_skips_tool_absent_from_tool_config():
    """Tools with no CONFIGURATION_ARGS (e.g. StopExecutionTool) won't have a tool_config entry — must not crash."""
    tool = MagicMock()
    tool.NAME = "stop_execution"
    agent = _StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {},
    })

    tool.set_runtime_arguments.assert_not_called()


def test_set_runtime_arguments_tolerates_missing_tool_config_key():
    """Old-format configs without a tool_config key must not crash."""
    tool = MagicMock()
    tool.NAME = "my_tool"
    agent = _StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
    })

    tool.set_runtime_arguments.assert_not_called()


def test_set_runtime_arguments_only_injects_matching_tool():
    """When multiple tools are present, only the matching one receives its config."""
    tool_a = MagicMock()
    tool_a.NAME = "tool_a"
    tool_b = MagicMock()
    tool_b.NAME = "tool_b"
    agent = _StubAgent(tools=[tool_a, tool_b])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {"tool_a": {"key": "value"}},
    })

    tool_a.set_runtime_arguments.assert_called_once_with({"key": "value"})
    tool_b.set_runtime_arguments.assert_not_called()
```

- [ ] **Step 1.2: Run tests to confirm they fail**

```bash
cd server && pytest agent/tests/test_runtime_arguments.py -v
```

Expected: all 4 tests fail — `pop("tools")` raises `KeyError` on the new config format.

- [ ] **Step 1.3: Implement named lookup in `set_runtime_arguments`**

In `plugins/enthusiast-common/enthusiast_common/agents/base.py`, replace lines 69–78:

```python
def set_runtime_arguments(self, runtime_arguments: Any) -> None:
    tool_config = runtime_arguments.pop("tool_config", {})
    for key, value in runtime_arguments.items():
        class_field_key = key.upper()
        field = getattr(self, class_field_key)
        if field is None:
            continue
        setattr(self, key.upper(), field(**value))
    for tool in self._tools:
        tool_runtime_args = tool_config.get(tool.NAME)
        if tool_runtime_args is not None:
            tool.set_runtime_arguments(tool_runtime_args)
```

- [ ] **Step 1.4: Run tests to confirm they pass**

```bash
cd server && pytest agent/tests/test_runtime_arguments.py -v
```

Expected: all 4 tests pass.

- [ ] **Step 1.5: Commit**

```bash
git add plugins/enthusiast-common/enthusiast_common/agents/base.py server/agent/tests/test_runtime_arguments.py
git commit -m "feat: replace positional tool config lookup with named lookup in set_runtime_arguments"
```

---

## Task 2: Update preconfiguration service — `tool_config` dict

**Files:**
- Modify: `server/agent/services/agent_preconfiguration_service.py:39-46`
- Modify: `server/agent/tests/test_services.py`

---

- [ ] **Step 2.1: Update `test_services.py` — add `NAME` to `DummyTool`, update expected config**

In `server/agent/tests/test_services.py`:

1. Add `NAME = "dummy_tool"` to `DummyTool` (line 11):

```python
class DummyTool(BaseFunctionTool):
    NAME = "dummy_tool"
    CONFIGURATION_ARGS = ToolArgs
```

2. Reduce `MockAgentClass.TOOLS` to one tool (two tools with the same `NAME` would produce one dict entry — simplify to one):

```python
class MockAgentClass:
    AGENT_KEY = "dummy_agent"
    NAME = "Dummy Agent"
    AGENT_ARGS = AgentArgs
    PROMPT_INPUT = PromptInput
    PROMPT_EXTENSION = PromptExtension
    TOOLS = [FunctionToolConfig(tool_class=DummyTool)]
    FILE_UPLOAD = False
```

3. Update `EXPECTED_AGENT_CONFIG` (line 34):

```python
EXPECTED_AGENT_CONFIG = {
    "agent_args": {"with_default": "default"},
    "prompt_extension": {"with_default": "default"},
    "prompt_input": {"with_default": "default"},
    "tool_config": {"dummy_tool": {"with_default": "default"}},
}
```

- [ ] **Step 2.2: Run to confirm test fails**

```bash
cd server && pytest agent/tests/test_services.py::TestAgentPreconfigurationService::test_preconfigure_available_agents_creates_agents -v
```

Expected: `AssertionError` — `agent.config` still contains `"tools": [...]`.

- [ ] **Step 2.3: Implement `tool_config` dict in `_build_default_agent_configuration`**

In `server/agent/services/agent_preconfiguration_service.py`, replace lines 39–47:

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

- [ ] **Step 2.4: Run all service tests**

```bash
cd server && pytest agent/tests/test_services.py -v
```

Expected: all tests pass.

- [ ] **Step 2.5: Commit**

```bash
git add server/agent/services/agent_preconfiguration_service.py server/agent/tests/test_services.py
git commit -m "feat: build tool_config dict in agent preconfiguration service"
```

---

## Task 3: Replace `PydanticModelToolListField` with `PydanticModelToolConfigField`

**Files:**
- Modify: `server/agent/serializers/customs/fields.py`
- Modify: `server/agent/serializers/customs/tests/test_fields.py`
- Modify: `server/agent/serializers/configuration.py`

---

- [ ] **Step 3.1: Update `test_fields.py` — replace list-based tests with dict-based tests**

Replace the full content of the tool list field test section in `server/agent/serializers/customs/tests/test_fields.py`.

First add `NAME` to `DummyTool` (line 12) and add a second tool class:

```python
class DummyTool(BaseFunctionTool):
    NAME = "dummy_tool"
    CONFIGURATION = DummySchema


class DummyTool2(BaseFunctionTool):
    NAME = "dummy_tool_2"
    CONFIGURATION = DummySchema
```

Update the import line (line 6) to import `PydanticModelToolConfigField` instead of `PydanticModelToolListField`:

```python
from agent.serializers.customs.fields import PydanticModelField, PydanticModelToolConfigField
```

Replace the helper factory and all tool list tests (lines 19-87) with:

```python
def get_tool_config_serializer(agent_field_name: str, tool_field_name: str, data: Any):
    class FieldTestSerializer(serializers.Serializer):
        config = PydanticModelToolConfigField(agent_field_name=agent_field_name, tool_field_name=tool_field_name)

    return FieldTestSerializer(data=data, context={"agent_type": "dummy_agent"})


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_valid(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool), FunctionToolConfig(tool_class=DummyTool2)]}
    )
    input_data = {"config": {"dummy_tool": {"value_1": "Alice", "value_2": 25}}}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    serializer.is_valid(raise_exception=True)

    assert serializer.data == input_data


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_invalid_type(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool)]}
    )
    input_data = {"config": [{"value_1": "Alice", "value_2": 25}]}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert "Expected a dict" in str(e.value)


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_unknown_tool_name(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool)]}
    )
    input_data = {"config": {"nonexistent_tool": {"value_1": "Alice", "value_2": 25}}}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert "Unknown tool" in str(e.value)


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_invalid_field_values(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool), FunctionToolConfig(tool_class=DummyTool2)]}
    )
    input_data = {"config": {
        "dummy_tool": {"value_1": "Missing value_2"},
        "dummy_tool_2": {"value_2": 99},
    }}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    serializer.is_valid()

    assert "dummy_tool" in serializer.errors["config"]
    assert "dummy_tool_2" in serializer.errors["config"]
```

- [ ] **Step 3.2: Run to confirm tests fail**

```bash
cd server && pytest agent/serializers/customs/tests/test_fields.py -v
```

Expected: `ImportError` — `PydanticModelToolConfigField` not yet defined.

- [ ] **Step 3.3: Implement `PydanticModelToolConfigField` in `fields.py`**

In `server/agent/serializers/customs/fields.py`, add after the existing `PydanticModelToolListField` class (after line 72):

```python
class PydanticModelToolConfigField(BasePydanticModelField):
    """Validates a tool_config dict keyed by tool NAME against each tool's CONFIGURATION_ARGS schema."""

    def __init__(self, *, agent_field_name: str, tool_field_name: str, **kwargs):
        self.agent_field_name = agent_field_name
        self.tool_field_name = tool_field_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        agent_type = self.context.get("agent_type")
        if not agent_type:
            raise AssertionError("Missing 'agent_type' in field context")

        try:
            class_obj = AgentRegistry().get_agent_class_by_type(agent_type)
            tool_config_list = getattr(class_obj, self.agent_field_name)
        except Exception as e:
            raise serializers.ValidationError(f"Error loading agent or field: {str(e)}")

        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected a dict of tool configurations.")

        tool_config_by_name = {
            tc.tool_class.NAME: tc
            for tc in tool_config_list
            if hasattr(tc.tool_class, "NAME")
        }

        validated = {}
        errors = {}
        has_errors = False

        for tool_name, tool_config_dict in data.items():
            if tool_name not in tool_config_by_name:
                errors[tool_name] = f"Unknown tool: {tool_name}"
                has_errors = True
                continue

            tool_config_obj = tool_config_by_name[tool_name]
            config_schema = getattr(tool_config_obj.tool_class, self.tool_field_name, None)
            if not config_schema or not isinstance(config_schema, type) or not issubclass(config_schema, BaseModel):
                validated[tool_name] = {}
                continue

            try:
                instance = config_schema(**tool_config_dict)
                validated[tool_name] = instance.model_dump()
            except PydanticValidationError as e:
                has_errors = True
                errors[tool_name] = self._format_pydantic_errors(e)

        if has_errors:
            raise serializers.ValidationError(errors)

        return validated

    def to_representation(self, value):
        if isinstance(value, dict):
            return {
                k: v.model_dump() if isinstance(v, BaseModel) else v
                for k, v in value.items()
            }
        return value

    class Meta:
        swagger_schema_fields = {"type": openapi.TYPE_OBJECT}
```

- [ ] **Step 3.4: Run field tests**

```bash
cd server && pytest agent/serializers/customs/tests/test_fields.py -v
```

Expected: all tests pass.

- [ ] **Step 3.5: Update `views.py` — build `tool_config` dict for the available agents endpoint**

In `server/agent/views.py` the GET `/api/agents/types` endpoint builds the data that `AgentChoiceSerializer` receives. Replace the `tools` list (around line 257) with a `tool_config` dict:

```python
"tool_config": {
    tool_config.tool_class.NAME: get_model_descriptor_from_class_field(
        tool_config.tool_class, "CONFIGURATION_ARGS"
    )
    for tool_config in agent_class.TOOLS
    if tool_config.tool_class.CONFIGURATION_ARGS is not None
},
```

The full `choices.append(...)` call becomes:

```python
choices.append(
    {
        "name": agent_class.NAME,
        "key": agent_class.AGENT_KEY,
        "agent_args": get_model_descriptor_from_class_field(agent_class, "AGENT_ARGS"),
        "prompt_input": get_model_descriptor_from_class_field(agent_class, "PROMPT_INPUT"),
        "prompt_extension": get_model_descriptor_from_class_field(agent_class, "PROMPT_EXTENSION"),
        "tool_config": {
            tool_config.tool_class.NAME: get_model_descriptor_from_class_field(
                tool_config.tool_class, "CONFIGURATION_ARGS"
            )
            for tool_config in agent_class.TOOLS
            if tool_config.tool_class.CONFIGURATION_ARGS is not None
        },
    }
)
```

- [ ] **Step 3.7: Update `configuration.py` — rename fields in both serializers**

In `server/agent/serializers/configuration.py`:

1. Update the import (line 7):

```python
from agent.serializers.customs.fields import PydanticModelField, PydanticModelToolConfigField
```

2. Update `AgentChoiceSerializer` (lines 11-17) — `tools` list → `tool_config` dict:

```python
class AgentChoiceSerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
    agent_args = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_input = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    prompt_extension = serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True)
    tool_config = serializers.DictField(
        child=serializers.DictField(child=ExtraArgDetailSerializer(), allow_empty=True),
        allow_empty=True,
    )
```

3. Update `AgentConfigSerializer` (lines 24-30) — `tools` → `tool_config`:

```python
class AgentConfigSerializer(ParentDataContextSerializerMixin, serializers.Serializer):
    context_keys_to_propagate = ["agent_type"]

    agent_args = PydanticModelField(agent_field_name="AGENT_ARGS")
    prompt_input = PydanticModelField(agent_field_name="PROMPT_INPUT")
    prompt_extension = PydanticModelField(agent_field_name="PROMPT_EXTENSION")
    tool_config = PydanticModelToolConfigField(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS")
```

- [ ] **Step 3.8: Run all backend tests**

```bash
cd server && pytest -v
```

Expected: all tests pass.

- [ ] **Step 3.9: Commit**

```bash
git add server/agent/serializers/customs/fields.py \
        server/agent/serializers/customs/tests/test_fields.py \
        server/agent/serializers/configuration.py \
        server/agent/views.py
git commit -m "feat: replace PydanticModelToolListField with PydanticModelToolConfigField"
```

---

## Task 4: Frontend — types + API client

**Files:**
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/api/agents.ts`

---

- [ ] **Step 4.1: Update `AgentConfig` type in `types.ts`**

In `frontend/src/lib/types.ts`, replace lines 89-90 (the `AgentConfig` type):

```typescript
export type AgentConfig = {
  agent_args?: Record<string, ExtraArgDetail>;
  prompt_input?: Record<string, ExtraArgDetail>;
  prompt_extension?: Record<string, ExtraArgDetail>;
  tool_config?: Record<string, Record<string, ExtraArgDetail>>;
};
```

- [ ] **Step 4.2: Update `AgentChoice` type in `agents.ts`**

In `frontend/src/lib/api/agents.ts`, replace lines 5-12:

```typescript
export type AgentChoice = {
  key: string;
  name: string;
  agent_args: Record<string, string>;
  prompt_inputs: Record<string, string>;
  prompt_extension: Record<string, string>;
  tool_config: Record<string, Record<string, string>>;
};
```

- [ ] **Step 4.3: Run TypeScript type-check**

```bash
cd frontend && pnpm build 2>&1 | head -60
```

Expected: type errors in `use-agent-form.ts` and `agent-configuration-form.tsx` that reference the old `tools` shape. These will be fixed in Task 5.

- [ ] **Step 4.4: Commit**

```bash
git add frontend/src/lib/types.ts frontend/src/lib/api/agents.ts
git commit -m "feat: update AgentConfig and AgentChoice types for tool_config dict schema"
```

---

## Task 5: Frontend — form-utils, hook, component

**Files:**
- Modify: `frontend/src/lib/form-utils.ts`
- Modify: `frontend/src/components/agents-table/hooks/use-agent-form.ts`
- Modify: `frontend/src/components/agents-table/agent-configuration-form.tsx`

---

- [ ] **Step 5.1: Update `flattenConfigForForm` in `form-utils.ts`**

In `frontend/src/lib/form-utils.ts`, replace the function body of `flattenConfigForForm` (lines 5-50) with:

```typescript
export function flattenConfigForForm(
  config: unknown,
  sectionMapping?: Record<string, string>
): Record<string, string | number | boolean> {
  const flattenedConfig: Record<string, string | number | boolean> = {};

  if (!config || typeof config !== 'object') {
    return flattenedConfig;
  }

  Object.entries(config as Record<string, unknown>).forEach(([section, sectionData]) => {
    const frontendSection = sectionMapping?.[section] || section;

    if (section === 'tool_config' && sectionData && typeof sectionData === 'object' && !Array.isArray(sectionData)) {
      // 2-level: {toolName: {fieldName: value}}
      Object.entries(sectionData as Record<string, Record<string, unknown>>).forEach(([toolName, toolFields]) => {
        if (toolFields && typeof toolFields === 'object') {
          Object.entries(toolFields).forEach(([key, value]) => {
            if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
              flattenedConfig[`${frontendSection}_${toolName}_${key}`] = value;
            }
          });
        }
      });
    } else if (Array.isArray(sectionData)) {
      sectionData.forEach(obj => {
        if (obj && typeof obj === 'object') {
          Object.entries(obj).forEach(([key, value]) => {
            if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
              flattenedConfig[`${frontendSection}_${key}`] = value;
            } else if (typeof value === 'object' && value !== null) {
              try {
                flattenedConfig[`${frontendSection}_${key}`] = JSON.stringify(value);
              } catch {
                flattenedConfig[`${frontendSection}_${key}`] = '{}';
              }
            }
          });
        }
      });
    } else if (sectionData && typeof sectionData === 'object') {
      Object.entries(sectionData).forEach(([key, value]) => {
        if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
          flattenedConfig[`${frontendSection}_${key}`] = value;
        } else if (typeof value === 'object' && value !== null) {
          try {
            flattenedConfig[`${frontendSection}_${key}`] = JSON.stringify(value);
          } catch {
            flattenedConfig[`${frontendSection}_${key}`] = '{}';
          }
        }
      });
    }
  });

  return flattenedConfig;
}
```

- [ ] **Step 5.2: Update `use-agent-form.ts` — default values, build, and error parsing**

In `frontend/src/components/agents-table/hooks/use-agent-form.ts`:

**A. Replace `createDefaultConfigValues` (lines 94-108):**

```typescript
const createDefaultConfigValues = (configSections: Record<string, unknown>) => {
  const defaults: Record<string, string | number | boolean> = {};
  Object.entries(configSections).forEach(([section, sectionData]) => {
    if (section === 'tool_config' && sectionData && typeof sectionData === 'object' && !Array.isArray(sectionData)) {
      Object.entries(sectionData as Record<string, Record<string, unknown>>).forEach(([toolName, toolFields]) => {
        if (toolFields && typeof toolFields === 'object') {
          Object.keys(toolFields).forEach(k => { defaults[`tool_config_${toolName}_${k}`] = ""; });
        }
      });
    } else if (Array.isArray(sectionData)) {
      sectionData.forEach(obj => {
        if (obj && typeof obj === 'object') {
          Object.keys(obj).forEach(k => { defaults[`${section}_${k}`] = ""; });
        }
      });
    } else if (sectionData && typeof sectionData === 'object') {
      Object.keys(sectionData).forEach(k => { defaults[`${section}_${k}`] = ""; });
    }
  });
  return defaults;
};
```

**B. Add `buildToolConfigDictConfig` helper before `buildNestedConfigFromFlattened` (before line 141):**

```typescript
const buildToolConfigDictConfig = (fields: Record<string, Record<string, unknown>>) => {
  const out: Record<string, Record<string, string | number | boolean>> = {};
  Object.entries(fields).forEach(([toolName, toolFields]) => {
    out[toolName] = {};
    if (toolFields && typeof toolFields === 'object') {
      Object.keys(toolFields).forEach(k => {
        const v = config[`tool_config_${toolName}_${k}`];
        if (v !== '' && v !== null && v !== undefined) out[toolName][k] = v;
      });
    }
  });
  return out;
};
```

**C. Replace `buildNestedConfigFromFlattened` (lines 141-151):**

```typescript
const buildNestedConfigFromFlattened = () => {
  const configObj: Record<string, unknown> = {};
  Object.entries(agentConfigSections).forEach(([section, fields]) => {
    if (section === 'tool_config' && fields && typeof fields === 'object' && !Array.isArray(fields)) {
      configObj[section] = buildToolConfigDictConfig(fields as Record<string, Record<string, unknown>>);
    } else if (Array.isArray(fields)) {
      configObj[section] = buildToolsArrayConfig(section, fields);
    } else if (fields && typeof fields === 'object') {
      configObj[section] = buildRegularSectionConfig(section, fields);
    }
  });
  return configObj;
};
```

**D. Replace `parseToolsArrayErrors` (lines 221-231) with `parseToolConfigErrors`:**

```typescript
const parseToolConfigErrors = (toolConfigErrors: unknown, newFieldErrors: Record<string, string>) => {
  if (toolConfigErrors && typeof toolConfigErrors === 'object' && !Array.isArray(toolConfigErrors)) {
    Object.entries(toolConfigErrors as Record<string, unknown>).forEach(([toolName, toolErrors]) => {
      if (toolErrors && typeof toolErrors === 'object') {
        Object.entries(toolErrors as Record<string, unknown>).forEach(([field, error]) => {
          newFieldErrors[`tool_config_${toolName}_${field}`] = Array.isArray(error) ? String(error[0]) : String(error);
        });
      }
    });
  }
};
```

**E. In `parseFieldErrors` (line 206), update the call from `parseToolsArrayErrors` to `parseToolConfigErrors`:**

```typescript
parseToolConfigErrors((configErrors as Record<string, unknown>).tool_config, newFieldErrors);
```

- [ ] **Step 5.3: Update `AgentConfigurationForm` — add `renderToolConfigFields`, update dispatch**

In `frontend/src/components/agents-table/agent-configuration-form.tsx`:

**A. Replace `checkForSectionErrors` inner body (lines 23-35) to handle `tool_config`:**

```typescript
const checkForSectionErrors = (section: string, fields: Record<string, unknown> | Record<string, unknown>[]) => {
  if (section === 'tool_config' && fields && typeof fields === 'object' && !Array.isArray(fields)) {
    return Object.entries(fields as Record<string, Record<string, unknown>>).some(([toolName, toolFields]) =>
      Object.keys(toolFields || {}).some(key => fieldErrors[`tool_config_${toolName}_${key}`])
    );
  }
  if (Array.isArray(fields)) {
    return fields.some(obj => {
      if (obj && typeof obj === 'object') {
        return Object.keys(obj).some(key => fieldErrors[`${section}_${key}`]);
      }
      return false;
    });
  } else if (fields && typeof fields === 'object') {
    return Object.keys(fields).some(key => fieldErrors[`${section}_${key}`]);
  }
  return false;
};
```

**B. Add `renderToolConfigFields` after `renderRegularFields` (after line 102):**

```tsx
const renderToolConfigFields = (fields: Record<string, Record<string, unknown>>) => {
  return Object.entries(fields).map(([toolName, toolFields]) => {
    const sFields = toolFields && typeof toolFields === 'object' ? toolFields : {};
    if (Object.keys(sFields).length === 0) return null;
    return (
      <div key={toolName} className="pl-4 border-l-2 border-muted bg-muted/20 rounded-r-md p-3">
        <div className="space-y-3">
          {Object.entries(sFields).map(([key, schema]) => {
            const configKey = `tool_config_${toolName}_${key}`;
            return typeof key === 'string' ? renderConfigField(key, schema, configKey) : null;
          })}
        </div>
      </div>
    );
  });
};
```

**C. Update `renderConfigSection` `hasFields` check and render dispatch (lines 103-131):**

```tsx
const renderConfigSection = (section: string, fields: Record<string, unknown> | Record<string, unknown>[]) => {
  let hasFields = false;
  if (section === 'tool_config' && !Array.isArray(fields) && fields && typeof fields === 'object') {
    hasFields = Object.values(fields as Record<string, Record<string, unknown>>).some(
      toolFields => toolFields && typeof toolFields === 'object' && Object.keys(toolFields).length > 0
    );
  } else if (Array.isArray(fields)) {
    hasFields = fields.some(obj => obj && typeof obj === 'object' && Object.keys(obj).length > 0);
  } else if (fields && typeof fields === 'object') {
    hasFields = Object.keys(fields).length > 0;
  }
  if (!hasFields) return null;

  const sectionTitle = String(section).replace(/_/g, ' ');

  return (
    <Collapsible
      key={section}
      open={openSections[section]}
      onOpenChange={(open) => setOpenSections({ ...openSections, [section]: open })}
    >
      <CollapsibleTrigger asChild>
        <Button variant="ghost" className="w-full justify-between p-0 h-auto">
          <div className="flex items-center gap-2">
            {openSections[section] ? <ChevronDownIcon className="h-4 w-4" /> : <ChevronRightIcon className="h-4 w-4" />}
            <span className="text-sm font-medium text-foreground capitalize">
              {sectionTitle}
            </span>
          </div>
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-4 mt-2">
        <div className="pl-4 space-y-4">
          {section === 'tool_config' && !Array.isArray(fields)
            ? renderToolConfigFields(fields as Record<string, Record<string, unknown>>)
            : Array.isArray(fields)
            ? renderToolsArrayFields(section, fields)
            : renderRegularFields(section, fields as Record<string, unknown>)}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};
```

- [ ] **Step 5.4: Run TypeScript type-check**

```bash
cd frontend && pnpm build 2>&1 | head -80
```

Expected: no type errors.

- [ ] **Step 5.5: Start dev server and manually test**

```bash
cd frontend && pnpm run dev
```

Open the app, navigate to an agent that has tool configuration (e.g. a catalog web import agent with a proxy field). Verify:
1. The `tool config` section appears in the agent edit form and shows the proxy field.
2. Updating the proxy value and saving sends `tool_config: {scrape_product_data: {proxy: "..."}}` in the request payload (check Network tab).
3. Reloading the form shows the saved proxy value.
4. Creating a new agent of a type with tool config shows default values in the form.

- [ ] **Step 5.6: Commit**

```bash
git add frontend/src/lib/form-utils.ts \
        frontend/src/components/agents-table/hooks/use-agent-form.ts \
        frontend/src/components/agents-table/agent-configuration-form.tsx
git commit -m "feat: update frontend to handle tool_config dict in agent configuration form"
```

---

## Task 6: Final backend tests + full test run

- [ ] **Step 6.1: Run full backend test suite**

```bash
cd server && pytest -v
```

Expected: all tests pass.

- [ ] **Step 6.2: Run frontend lint**

```bash
cd frontend && pnpm run lint
```

Expected: no lint errors.
