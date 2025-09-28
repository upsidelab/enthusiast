---
sidebar_position: 4
---

# Tools

Tools in Enthusiast are modular components that extend agent capabilities by providing specific functionalities. They follow a standardized architecture that ensures consistency, validation, and easy integration with the LangChain ecosystem.

## Overview

Tools serve as the building blocks for agent functionality, allowing agents to:
- Search and retrieve information
- Process data and generate content
- Interact with external systems
- Perform specific business logic operations

Each tool is a self-contained unit with defined inputs, outputs, and execution logic that can be easily integrated into agent workflows.

## Architecture

### Base Classes

The tool system is built on a hierarchy of base classes that provide common functionality and validation:

#### `BaseTool` (Core Base Class)

The foundation for all tools in the system, providing:

- **Automatic validation** of required class variables
- **Standardized interface** for tool execution
- **LangChain integration** through the `as_tool()` method
- **Configuration management** for runtime arguments

#### `BaseFunctionTool`

A simple base class for tools that don't require additional dependencies. Inherits from `BaseTool` and provides basic tool functionality.

#### `BaseLLMTool`

Extends `BaseTool` with language model capabilities and injector access:

- **Language Model Integration**: Access to LLM instances for AI-powered operations
- **Injector Pattern**: Dependency injection for data access and external services
- **Dataset Context**: Awareness of the current dataset being processed

#### `BaseAgentTool`

Enables tools to call and interact with other agents, creating a hierarchical agent architecture:

- **Agent Orchestration**: Call other agents to perform specific tasks
- **Multi-Agent Workflows**: Coordinate complex operations across multiple agents
- **Agent Delegation**: Delegate specialized tasks to appropriate agent types

## Required Class Variables

All tools must define these class variables to ensure proper validation and functionality:

### `NAME` (str)
A unique identifier for the tool. Used by agents to reference and call the tool.

**Example:**
```python
NAME = "example_tool_name"
```

### `DESCRIPTION` (str)
A clear description of what the tool does and when to use it. This is crucial for agents to understand tool selection.

**Example:**
```python
DESCRIPTION = "Description of what this tool does and when to use it"
```

### `ARGS_SCHEMA` (Type[BaseModel])
A Pydantic model defining the input parameters the tool accepts. Ensures type safety and provides clear documentation of expected inputs.

**Example:**
```python
class ExampleToolInput(BaseModel):
    input_field: str = Field(description="Description of the input field")

ARGS_SCHEMA = ExampleToolInput
```

### `RETURN_DIRECT` (bool)
Controls whether the tool's output should be returned directly to the user or processed further by the agent.

- **`True`**: Output is returned directly to the user
- **`False`**: Output is processed by the agent for further reasoning

**Example:**
```python
RETURN_DIRECT = False
```

### `CONFIGURATION_ARGS` (RequiredFieldsModel or None)
Optional configuration parameters that can be set at runtime. If not needed, set to `None`.

**Example:**
```python
CONFIGURATION_ARGS = None
```

**With Configuration:**
```python
from pydantic import Field

class ConfigArgs(RequiredFieldsModel):
    max_retries: int = Field(title="Max Retries", description="Maximum number of retry attempts for failed operations", default=3)
    timeout_seconds: int = Field(title="Timeout", description="Timeout duration in seconds for operations", default=30)
    enable_logging: bool = Field(title="Enable Logging", description="Whether to enable detailed logging during execution", default=True)

CONFIGURATION_ARGS = ConfigArgs
```

**Accessing in run method:**
```python
def run(self, input_data: str):
    # Access configuration values
    max_retries = self.CONFIGURATION_ARGS.max_retries
    timeout = self.CONFIGURATION_ARGS.timeout_seconds
    logging_enabled = self.CONFIGURATION_ARGS.enable_logging
    
    # Use configuration in tool logic
    return self._process_with_config(input_data, max_retries, timeout, logging_enabled)
```

## Tool Implementation Examples

### Basic Tool Structure

```python
class ExampleTool(BaseLLMTool):
    NAME = "example_tool"
    DESCRIPTION = "Description of what this tool does"
    ARGS_SCHEMA = ExampleToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = None

    def __init__(self, data_set_id: int, llm: BaseLanguageModel, injector: BaseInjector):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.llm = llm
        self.injector = injector

    def run(self, input_field: str):
        # Tool implementation logic here
        result = self._process_input(input_field)
        return result
```

### Tool with Configuration Arguments

```python
from pydantic import Field
# Define configuration schema
class ConfigArgs(RequiredFieldsModel):
    batch_size: int = Field(title="Batch Size", description="Number of items to process in each batch", default=12)
    processing_mode: str = Field(title="Processing Mode", description="Mode of operation: 'fast', 'standard', or 'thorough'")
    enable_validation: bool = Field(title="Enable Validation", description="Whether to perform data validation during processing")
    output_format: str = Field(title="Output Format", description="Desired output format: 'json', 'xml', 'csv', or 'text'")

class ConfigurableTool(BaseLLMTool):
    NAME = "configurable_tool"
    DESCRIPTION = "Tool that uses runtime configuration arguments"
    ARGS_SCHEMA = ExampleToolInput
    RETURN_DIRECT = False
    CONFIGURATION_ARGS = ConfigArgs

    def run(self, input_data: str):
        # Access configuration arguments in the run method
        batch_size = self.CONFIGURATION_ARGS.batch_size
        processing_mode = self.CONFIGURATION_ARGS.processing_mode
        validation_enabled = self.CONFIGURATION_ARGS.enable_validation
        output_format = self.CONFIGURATION_ARGS.output_format
        
        # Use configuration values in tool logic
        if validation_enabled:
            logging.info(f"Processing in {processing_mode} mode with batch size {batch_size}")
        
        # Implementation using configuration
        result = self._process_with_config(
            input_data, 
            batch_size=batch_size,
            mode=processing_mode,
            validate=validation_enabled,
            format=output_format
        )
        
        return result
```

## Integration with LangChain

Tools automatically integrate with the LangChain ecosystem through the `as_tool()` method, which by default converts the tool into a `StructuredTool` that can be:

- **Used by agents** for task execution
- **Chained together** in complex workflows
- **Monitored and logged** through LangChain's observability features
