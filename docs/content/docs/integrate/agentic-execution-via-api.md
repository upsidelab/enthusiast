---
sidebar_position: 4
---

# Run an Agentic Execution via the API

Agentic executions are autonomous agent jobs submitted programmatically and polled for results. Unlike conversations, there is no back-and-forth — you submit input, wait for the job to finish, and retrieve structured output.

## List Available Execution Types

Before starting an execution, retrieve the execution types registered for the chosen agent. The response includes the input schema for each type, which you use to construct a valid request body.

```http
GET /api/agents/{agent_id}/agentic-execution-definitions/
Authorization: Token <your-token>
```

**Response:**
```json
[
  {
    "key": "catalog-enrichment",
    "name": "Catalog Enrichment",
    "description": null,
    "input_schema": {
      "title": "CatalogEnrichmentAgenticExecutionInput",
      "description": "Input for the catalog enrichment agentic execution.",
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "additional_instructions": {
          "title": "Additional Instructions",
          "anyOf": [{ "type": "string" }, { "type": "null" }],
          "default": null
        },
        "skus": {
          "title": "Skus",
          "anyOf": [{ "items": { "type": "string" }, "type": "array" }, { "type": "null" }],
          "default": null
        }
      }
    }
  }
]
```

Returns an empty list if no execution types are registered for the agent. Returns 404 if the agent does not exist.

## Start an Execution

```http
POST /api/agents/{agent_id}/agentic-executions/
Content-Type: application/json
Authorization: Token <your-token>

{
  "execution_key": "catalog-enrichment",
  "input": {
    "additional_instructions": "Focus on products missing a description.",
    "skus": ["SKU-001", "SKU-002"]
  }
}
```

**Response (`202 Accepted`):**
```json
{
  "id": 42,
  "agent": 7,
  "execution_key": "catalog-enrichment",
  "conversation": 198,
  "status": "pending",
  "input": {
    "additional_instructions": "Focus on products missing a description.",
    "skus": ["SKU-001", "SKU-002"]
  },
  "result": null,
  "failure_code": null,
  "failure_explanation": null,
  "celery_task_id": "debf5bf6-3e58-4c7d-9e30-c5a4055d951f",
  "started_at": "2025-04-10T14:00:00.000000Z",
  "finished_at": null,
  "duration_seconds": null,
  "files": [
    {
      "id": 4,
      "filename": "product_data.pdf",
      "file_url": "/media/conversations/198/product_data.pdf",
      "content_type": "application/pdf"
    }
  ]
}
```

Returns 400 if `execution_key` is unknown or belongs to a different agent type, or if `input` fails validation against the execution type's schema. Returns 404 if the agent does not exist.

### Sending Files

If the selected agent has file upload enabled, you can attach files using `multipart/form-data`. The `input` field must be a JSON-encoded string in this case.

```http
POST /api/agents/{agent_id}/agentic-executions/
Content-Type: multipart/form-data
Authorization: Token <your-token>

input={"additional_instructions": "Focus on products missing a description."}
files[]=@product_data.pdf
```

Sending files to an agent with file upload disabled returns 400. Unsupported file types are also rejected with 400.

## Get Execution

```http
GET /api/agentic-executions/{execution_id}/
Authorization: Token <your-token>
```

**Response (in progress):**
```json
{
  "id": 42,
  "agent": 7,
  "execution_key": "catalog-enrichment",
  "conversation": 198,
  "status": "in_progress",
  "input": { "skus": ["SKU-001", "SKU-002"], "additional_instructions": null },
  "result": null,
  "failure_code": null,
  "failure_explanation": null,
  "celery_task_id": "debf5bf6-3e58-4c7d-9e30-c5a4055d951f",
  "started_at": "2025-04-10T14:00:00.000000Z",
  "finished_at": null,
  "duration_seconds": null,
  "files": [
    {
      "id": 4,
      "filename": "product_data.pdf",
      "file_url": "/media/conversations/198/product_data.pdf",
      "content_type": "application/pdf"
    }
  ]
}
```

**Response (finished):**
```json
{
  "id": 42,
  "agent": 7,
  "execution_key": "catalog-enrichment",
  "conversation": 198,
  "status": "finished",
  "input": { "skus": ["SKU-001", "SKU-002"], "additional_instructions": null },
  "result": {
    "SKU-001": "Product updated successfully",
    "SKU-002": "Product updated successfully"
  },
  "failure_code": null,
  "failure_explanation": null,
  "celery_task_id": "debf5bf6-3e58-4c7d-9e30-c5a4055d951f",
  "started_at": "2025-04-10T14:00:00.000000Z",
  "finished_at": "2025-04-10T14:00:16.000000Z",
  "duration_seconds": 16.554571,
  "files": [
    {
      "id": 4,
      "filename": "product_data.pdf",
      "file_url": "/media/conversations/198/product_data.pdf",
      "content_type": "application/pdf"
    }
  ]
}
```

**Response (failed):**
```json
{
  "id": 42,
  "agent": 7,
  "execution_key": "catalog-enrichment",
  "conversation": 198,
  "status": "failed",
  "input": { "skus": ["SKU-001", "SKU-002"], "additional_instructions": null },
  "result": null,
  "failure_code": "validation_failed",
  "failure_explanation": "No product data found for SKU SKU-002 in any available resource.",
  "celery_task_id": "debf5bf6-3e58-4c7d-9e30-c5a4055d951f",
  "started_at": "2025-04-10T14:00:00.000000Z",
  "finished_at": "2025-04-10T14:00:18.000000Z",
  "duration_seconds": 18.230887,
  "files": [
    {
      "id": 4,
      "filename": "product_data.pdf",
      "file_url": "/media/conversations/198/product_data.pdf",
      "content_type": "application/pdf"
    }
  ]
}
```

### Failure codes

| Code | Meaning |
|------|---------|
| `runtime_error` | An unexpected error occurred during execution |
| `max_retries_exceeded` | The LLM failed to pass validators after the maximum number of correction cycles |
| `validation_failed` | A validator rejected the response without allowing a retry |
| `unknown` | Execution reported failure but returned no structured failure code |

Individual execution definitions may register additional domain-specific failure codes.

## List Executions

```http
GET /api/agentic-executions/
Authorization: Token <your-token>
```

Supports `agent_id`, `status` (`pending`, `in_progress`, `finished`, `failed`), and `dataset_id` as query parameters. Results are paginated (25 per page) and ordered newest first.

## Authentication

All endpoints require authentication. Read more about [connecting with the API](/docs/integrate/connect-to-api).
