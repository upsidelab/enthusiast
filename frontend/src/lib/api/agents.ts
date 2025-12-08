import {BaseApiClient} from "@/lib/api/base.ts";
import {Agent, AgentConfig, AgentDetails} from "@/lib/types.ts";
import {ApiError} from "@/lib/api-error.ts";

export type AgentChoice = {
  key: string;
  name: string;
  agent_args: Record<string, string>;
  prompt_inputs: Record<string, string>;
  prompt_extension: Record<string, string>;
  tools: Record<string, string>[];
  type: string;
};

type AvailableAgentsResponse = {
  choices: AgentChoice[];
};

export class AgentsApiClient extends BaseApiClient {
    async getAvailableAgentTypes(): Promise<AgentChoice[]> {
        const response = await fetch(`${this.apiBase}/api/agents/types`, this._requestConfiguration());

        if (!response.ok) {
            throw new Error(`Failed to fetch available agents: ${response.statusText}`);
        }

        const result = await response.json() as AvailableAgentsResponse;
        return result.choices;
    }
    async getDatasetAvailableAgents(dataSetId: number): Promise<Agent[]> {
        const query = new URLSearchParams({ dataset: dataSetId.toString() });
        const response = await fetch(
            `${this.apiBase}/api/agents?${query.toString()}`,
            this._requestConfiguration()
        );

        if (!response.ok) {
            throw new Error(`Failed to fetch available agents: ${response.statusText}`);
        }

        return await response.json() as Agent[];
    }
    async getAgentById(agentId: number): Promise<AgentDetails> {
        const response = await fetch(`${this.apiBase}/api/agents/${agentId}`, this._requestConfiguration());
        if (!response.ok) {
            throw new Error(`Failed to fetch agent: ${response.statusText}`);
        }
        return await response.json() as AgentDetails;
    }

    async createAgent(data: { name: string; agent_type: string; dataset: number; config: AgentConfig }): Promise<AgentDetails> {
        const response = await fetch(`${this.apiBase}/api/agents`, {
            ...this._requestConfiguration(),
            method: 'POST',
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new ApiError(`Failed to create agent: ${response.statusText}`, {
                data: errorData,
                status: response.status
            });
        }
        return await response.json() as AgentDetails;
    }

    async updateAgent(agentId: number, data: { name: string; agent_type: string; dataset: number; config: AgentConfig }): Promise<AgentDetails> {
        const response = await fetch(`${this.apiBase}/api/agents/${agentId}`, {
            ...this._requestConfiguration(),
            method: 'PUT',
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new ApiError(`Failed to update agent: ${response.statusText}`, {
                data: errorData,
                status: response.status
            });
        }
        return await response.json() as AgentDetails;

    }

    async deleteAgent(agentId: number): Promise<void> {
        const response = await fetch(`${this.apiBase}/api/agents/${agentId}`, {
            ...this._requestConfiguration(),
            method: 'DELETE',
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new ApiError(`Failed to delete agent: ${response.statusText}`, {
                data: errorData,
                status: response.status
            });
        }
    }
}
