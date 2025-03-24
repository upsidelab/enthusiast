---
sidebar_position: 3
---

# Run a Conversation via the API

## Create a Conversation

To start a new conversation, send a POST request to create a conversation with a specific data set.

```http
POST /api/conversations
Content-Type: application/json

{
  "data_set_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "started_at": "2025-03-20T10:00:00Z"
}
```

The response includes:
- `id`: The unique identifier for your new conversation
- `started_at`: Timestamp when the conversation was created

## Send a Message

Once you have the conversation id in place, you can send new messages to it.

```http
POST /api/conversations/{conversation_id}
Content-Type: application/json

{
  "question_message": "Does FiberUP Business Duplex include an SLA?",
  "data_set_id": 1
}
```

**Response:**
```json
{
  "task_id": "dbe41a42-f678-40c7-8b4c-437fa1673d7d"
}
```

The response includes a `task_id` that you can use to check the status of your message processing. The message processing happens asynchronously.

## Check the Processing Status

The task status endpoint allows you to check the progress of your message processing:

```http
GET /api/task_status/{task_id}
```

**Response:**
```json
{
  "state": "SUCCESS"
}
```

The `state` field will be one of:
- `PENDING`: The message is still being processed
- `SUCCESS`: The message has been processed successfully
- `FAILURE`: The message processing failed

You should poll this endpoint periodically (e.g., every 2 seconds) until you receive either `SUCCESS` or `FAILURE`. Once you receive `SUCCESS`, you can fetch the updated conversation to see the agent's response.

## Get Messages

To retrieve all messages from an existing conversation:

```http
GET /api/conversations/{conversation_id}
```

**Response:**
```json
{
  "id": 1,
  "started_at": "2025-03-20T10:00:00Z",
  ...
  "history": [
    {
      "id": 1,
      "text": "Does FiberUP Business Duplex include an SLA?",
      "role": "user"
    },
    {
      "id": 2,
      "text": "Yes, the plan includes an SLA with an optional priority support package ....",
      "role": "agent"
    }
  ]
}
```

The response includes:
- Conversation details (id, started_at, summary)
- `history`: Array of messages, each containing:
  - `id`: Unique message identifier
  - `text`: The message content
  - `role`: Either "user" (your messages) or "agent" (system responses)

## Authentication

All API endpoints require authentication. Read more about [authenticating with the API](/tools/enthusiast/docs/integrate/connect-to-api)