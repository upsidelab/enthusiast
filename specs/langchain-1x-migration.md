# LangChain 0.3 → 1.2.x Migration

## Summary

Full migration from LangChain 0.3.x to 1.2.x. All packages were updated to native 1.x patterns.

---

## Phase 1 — Dependency Bumps

Version constraints updated in all `pyproject.toml` files across server and plugins. No logic changes.

---

## Phase 2 — Memory System Migration

The old `langchain.memory` classes (`ConversationBufferMemory`, `ConversationTokenBufferMemory`, `ConversationSummaryBufferMemory`) and the `BaseMemory` interface are gone in 1.x.

**What was removed:**
- `LimitedChatMemory`, `SummaryChatMemory`, `PersistIntermediateStepsMixin` — all deleted
- `BaseInjector` properties `chat_summary_memory` / `chat_limited_memory` → replaced with single `chat_history: BaseChatMessageHistory`

**`FunctionMessage` → `ToolMessage`:**
`FunctionMessage` is the older schema without `tool_call_id`. `ToolMessage` is its replacement and carries `tool_call_id`, which LLM APIs (OpenAI, Anthropic) require to associate tool results with the specific parallel tool call that produced them. Since `create_agent` (LangGraph) can emit an `AIMessage` with multiple `tool_calls` in a single turn, history loaded back from DB must use `ToolMessage` with correct `tool_call_id` values or the API rejects it. A DB migration (`0027`) was added to store `tool_call_id` on message records and includes a data migration (`backfill_tool_call_messages`) that patches existing records for backward compatibility: legacy `INTERMEDIATE_STEP` / `FUNCTION` pairs are matched in conversation order, assigned a shared UUID `tool_call_id`, and `function_name` is copied from the `FUNCTION` record to the `INTERMEDIATE_STEP` record where missing. `Message.MessageType.FUNCTION` and the `langchain_type` property were updated accordingly.

**`PersistentChatHistory` updated:**
`add_message` now handles `AIMessage` with `tool_calls` (→ `INTERMEDIATE_STEP` records, one per tool call) and `ToolMessage` (→ `FUNCTION` record). The 1:1 pairing invariant is maintained inside the history class, not in the agent.

**Token limiting:**
`trim_messages` from `langchain_core.messages` replaces `ConversationTokenBufferMemory`. Called explicitly in `BaseToolCallingAgent._build_limited_history` before each invocation.

---

## Phase 3 — LangGraph Agent Migration

`AgentExecutor` and `create_tool_calling_agent` are fully removed in 1.2.x — not deprecated, gone. The only agent API is `create_agent` from `langchain.agents`, backed by LangGraph (`CompiledStateGraph`).

**Invocation pattern:**
`create_agent` takes `model`, `tools`, and a static `system_prompt` string. It receives and returns the full message list. New messages are extracted by slicing `result["messages"][len(input_messages):]`. Intermediate tool calls and results appear directly in the message list as `AIMessage(tool_calls=[...])` + `ToolMessage` pairs — no separate `intermediate_steps` key.

**System prompt / config simplification:**
`ChatPromptTemplate` is no longer used for agent configuration. The full `AgentConfig.prompt_template: ChatPromptTemplateConfig` field was replaced with `system_prompt: str`. `BaseAgent.__init__` now takes `system_prompt: str` (stored as `self._system_prompt`) instead of `prompt: ChatPromptTemplate`. `BaseAgent` exposes a `_get_system_prompt_variables() -> dict` hook (returns `{}` by default) for agents whose system prompt contains template variables. `BaseAgentBuilder._build_prompt_template` was removed entirely. All plugin `config.py` files were simplified to pass `system_prompt=` directly. `enthusiast_common/config/prompts.py` (`ChatPromptTemplateConfig`, `Message`, `MessageRole`) was fully removed. `FileRetrievalTool` was refactored to build `SystemMessage`/`HumanMessage` directly instead of going through `ChatPromptTemplateConfig`.

**History persistence:**
After `invoke()`, new messages are written in one call via `history.add_messages(new_messages)`. `new_messages` is sliced from after `limited_history` (not after the full `input_messages`), so it includes the human message, all tool call/result pairs, and the final AI response. The splitting of multi-tool-call `AIMessage`s into individual `INTERMEDIATE_STEP` records is handled inside `PersistentChatHistory._create_intermediate_step_message`.

---

## Phase 4 — Callback / WebSocket Cleanup

**Problem:** `on_chain_start` / `on_chain_end` were the original lifecycle hooks (0.3, `AgentExecutor`-era). They fired once per agent turn. In LangGraph they fire for every graph node, making them useless as turn-level signals. They never actually fired in production because the handler was registered on the LLM instance, not on the agent/graph (they actually fired only for ReAct Agents since they configured handler on agent, not on LLM, and since their deprecation those callbacks became dead code).

**Decision:** `ConversationWebSocketCallbackHandler` now handles only `on_llm_new_token` (with a falsy-token guard). Start/end events are no longer sent over WebSocket.

**Frontend:** The `on_parser_start` handler was removed from `chat-session.tsx` — it was redundant since `isAgentLoading` is already set on message submit. `on_parser_end` had no handler and was never sent. The WebSocket connection is session-scoped (one connection per chat session, reused across messages, closed on navigation away).
