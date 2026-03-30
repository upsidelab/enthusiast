import { BaseApiClient } from "@/lib/api/base.ts";
import { AgentExecution, AgentExecutionDetail, ExecutionType, PaginatedResult } from "@/lib/types.ts";

export class AgentExecutionsApiClient extends BaseApiClient {
  async list(filters?: { datasetId?: number; agentId?: number; status?: string }, page: number = 1): Promise<PaginatedResult<AgentExecution>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters?.datasetId) params.set("dataset_id", filters.datasetId.toString());
    if (filters?.agentId) params.set("agent_id", filters.agentId.toString());
    if (filters?.status) params.set("status", filters.status);
    const response = await fetch(`${this.apiBase}/api/agent-executions/?${params}`, this._requestConfiguration());
    return await response.json() as PaginatedResult<AgentExecution>;
  }

  async get(id: number): Promise<AgentExecutionDetail> {
    const response = await fetch(`${this.apiBase}/api/agent-executions/${id}/`, this._requestConfiguration());
    return await response.json() as AgentExecutionDetail;
  }

  async getTypes(agentId: number): Promise<ExecutionType[]> {
    const response = await fetch(`${this.apiBase}/api/agents/${agentId}/execution-types/`, this._requestConfiguration());
    return await response.json() as ExecutionType[];
  }
}
