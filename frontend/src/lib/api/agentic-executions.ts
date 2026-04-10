import { BaseApiClient } from "@/lib/api/base.ts";
import { AgenticExecution, AgenticExecutionDetail, ExecutionType, PaginatedResult } from "@/lib/types.ts";
import { ApiError } from "@/lib/api-error.ts";

export class AgenticExecutionsApiClient extends BaseApiClient {
  async list(filters?: { datasetId?: number; agentId?: number; status?: string }, page: number = 1): Promise<PaginatedResult<AgenticExecution>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters?.datasetId) params.set("dataset_id", filters.datasetId.toString());
    if (filters?.agentId) params.set("agent_id", filters.agentId.toString());
    if (filters?.status) params.set("status", filters.status);
    const response = await fetch(`${this.apiBase}/api/agentic-executions/?${params}`, this._requestConfiguration());
    return await response.json() as PaginatedResult<AgenticExecution>;
  }

  async get(id: number): Promise<AgenticExecutionDetail> {
    const response = await fetch(`${this.apiBase}/api/agentic-executions/${id}/`, this._requestConfiguration());
    return await response.json() as AgenticExecutionDetail;
  }

  async getTypes(agentId: number): Promise<ExecutionType[]> {
    const response = await fetch(`${this.apiBase}/api/agents/${agentId}/agentic-execution-definitions/`, this._requestConfiguration());
    return await response.json() as ExecutionType[];
  }

  async create(agentId: number, data: { execution_key: string; input: Record<string, unknown>; files?: File[] }): Promise<AgenticExecution> {
    const { execution_key, input, files } = data;
    let response: Response;

    if (files && files.length > 0) {
      const formData = new FormData();
      formData.append("execution_key", execution_key);
      formData.append("input", JSON.stringify(input));
      files.forEach(file => formData.append("files", file));

      const requestConfig = this._requestConfiguration();
      const headers = { ...requestConfig.headers } as Record<string, string>;
      delete headers["Content-Type"];

      response = await fetch(`${this.apiBase}/api/agents/${agentId}/agentic-executions/`, {
        ...requestConfig,
        method: "POST",
        headers,
        body: formData,
      });
    } else {
      response = await fetch(`${this.apiBase}/api/agents/${agentId}/agentic-executions/`, {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({ execution_key, input }),
      });
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(`Failed to create agentic execution: ${response.statusText}`, {
        data: errorData,
        status: response.status,
      });
    }

    return await response.json() as AgenticExecution;
  }
}
