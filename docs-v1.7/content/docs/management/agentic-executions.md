# Agentic Executions

The Agentic Executions section gives you visibility into all autonomous agent jobs triggered for your data set — their status, results, and the internal conversation log produced during each run.

## History Dashboard

Navigate to **Configure** → **Agentic Executions** in the left sidebar to reach the history dashboard.

The dashboard lists all past executions for the current data set, newest first. You can filter the list by:
- **Agent** — narrow to executions from a specific configured agent
- **Status** — filter by `pending`, `in_progress`, `finished`, or `failed`

Filter state is preserved in the URL, so the view survives a page refresh and can be bookmarked or shared.

## Launching an Execution

Click **New Execution** to open the launch form. The form walks through three steps:

1. **Select an agent** — choose from agents configured for the current data set.
2. **Select an execution type** — after choosing an agent, the available execution types are populated dynamically from the server. Each type shows a name and description to help you pick the right one.
3. **Provide input** — fill in the fields derived from the execution type's input schema. If the selected agent supports file uploads, a file attachment field also appears.

Field-level validation errors and API errors are displayed inline. On success, you are taken directly to the new execution's detail view.

## Execution Detail View

The detail view shows the full record for a single execution:

- **Status** — refreshes every 3 seconds while the execution is running. Polling stops automatically once a terminal state (`finished` or `failed`) is reached.
- **Result** — shown for finished executions: the structured JSON output returned by the execution definition.
- **Failure details** — shown for failed executions: the failure code and the LLM-generated explanation of what went wrong.
- **Conversation link** — a link to the internal conversation created for this execution, giving full visibility into the agent's message loop, tool calls, and intermediate reasoning.

## Execution Conversations

Each agentic execution creates an internal conversation to drive the agent's message loop. These conversations do not appear in the standard agent conversation history — they represent an implementation detail, not a user-initiated dialogue.

You can inspect an execution's conversation via the link on the detail view. The conversation is read-only: the text input and send button are disabled, with the placeholder "This conversation is read-only."
