import { BaseApiClient } from "@/lib/api/base.ts";
import { AgenticExecution, AgenticExecutionDetail, ExecutionType, PaginatedResult } from "@/lib/types.ts";

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
}
