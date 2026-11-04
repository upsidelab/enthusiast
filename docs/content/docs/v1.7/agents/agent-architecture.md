---
sidebar_position: 7
---

# Agent Architecture

The Enthusiast framework provides a comprehensive and modular agent architecture that enables the creation of sophisticated, tool-using AI agents. This document describes the core components and their relationships within the agent system.

## Overview

The agent architecture follows a layered design pattern that separates concerns and promotes modularity:

- **Core Agent Layer**: Defines the agent interface and behavior
- **Component Layer**: Provides specialized services (memory, tools, injector)
- **Builder Layer**: Handles agent construction and configuration
- **Configuration Layer**: Manages agent settings and dependencies

## Core Components

### 1. Base Agent

The foundation of all agents in the system.

**Purpose**: Defines the common interface and behavior that all agents must implement.

**Responsibilities**:
- Process user input and generate responses
- Manage tool execution and results
- Handle conversation context and state
- Coordinate with memory and injector systems

### 2. Injector

Dependency injection container that provides access to external resources.

**Purpose**: Centralizes resource management and provides clean interfaces for agents and tools.

**Available Resources**:
- **Document Retriever**: Access to document search and retrieval
- **Product Retriever**: Access to product catalog and search
- **Repositories**: Data access layer for all entities
- **Memory Systems**: Chat memory and conversation history

**Responsibilities**:
- Manage resource lifecycle
- Provide clean interfaces to external services
- Handle resource configuration and initialization
- Coordinate between different resource types

### 3. Tools

Extend agent capabilities through specialized functions and services.

**Types**:
- **Function Tools**: Simple operations
- **LLM Tools**: AI-powered operations with language models
- **Agent Tools**: Tools that use other agents

**Responsibilities**:
- Execute specific operations and tasks
- Provide results to agents
- Handle errors and edge cases

### 4. Memory

Manages conversation history and optional context compaction.

**Purpose**: Persists chat history across turns and, when enabled, compacts older context using an LLM to keep prompts within token limits.

**Components**:
- **Persistent Chat History**: Stores conversation messages in the database
- **Memory Compactor**: Summarizes older messages when the history grows too long

**Responsibilities**:
- Maintain conversation state between turns
- Reduce prompt size through summarization
- Provide history to agents on each request

### 5. Builder

Orchestrates the construction of fully configured agent instances.

**Purpose**: Manages the complex process of creating agents with all their dependencies.

**Construction Process**:
1. **Registry Building**: Create model and provider registries
2. **Repository Setup**: Initialize data access layer
3. **Component Assembly**: Build tools, memory, and injector
4. **Agent Instantiation**: Create and configure the agent
5. **Runtime Configuration**: Apply dynamic configuration

**Responsibilities**:
- Coordinate component construction
- Manage dependency resolution
- Handle configuration validation
- Ensure proper component initialization

### 6. System Prompt

Defines agent behavior, instructions, and reasoning patterns.

**Purpose**: A plain string provided via `AgentConfig.system_prompt` that shapes how the agent behaves, what tools it uses, and how it responds.

**Responsibilities**:
- Guide agent behavior and reasoning
- Provide tool usage instructions
- Define conversation patterns
- Establish output constraints

### 7. Configuration

Manages agent settings, dependencies, and runtime parameters.

**Components**:
- **AgentConfig**: Core agent configuration including system prompt and memory settings
- **LLMConfig**: Language model settings
- **FunctionToolConfig / LLMToolConfig / AgentToolConfig / FileToolConfig**: Per-tool-type configurations
- **RepositoriesConfig**: Data access layer configuration
- **RetrieversConfig**: Document and product retriever configuration

**Responsibilities**:
- Define agent capabilities and settings
- Manage component configurations
- Validate configuration integrity
- Support runtime customization

## Summary

The Enthusiast agent architecture provides a robust, flexible, and extensible foundation for building sophisticated AI agents:

- **Modular Design**: Clear separation of concerns and responsibilities
- **Dependency Injection**: Clean, testable component integration
- **Configuration-Driven**: Flexible and customizable agent behavior
- **Extensible**: Easy to add new capabilities and components
- **Robust**: Built-in error handling and recovery mechanisms

By understanding and following the established patterns, developers can create powerful, maintainable, and scalable agent systems that leverage the full capabilities of the Enthusiast framework.
