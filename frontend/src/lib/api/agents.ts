import {BaseApiClient} from "@/lib/api/base.ts";
import {AgentInstance} from "@/lib/types.ts";

type AgentChoice = {
  key: string;
  name: string;
  agent_args: Record<string, string>;
  prompt_inputs: Record<string, string>;
  prompt_extension: Record<string, string>;
  tools: Record<string, string>[];
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
    async getDatasetAvailableAgents(dataSetId: number): Promise<AgentInstance[]> {
   const response = await fetch(`${this.apiBase}/api/agents/dataset/${dataSetId}`, this._requestConfiguration());

    if (!response.ok) {
      throw new Error(`Failed to fetch available agent instances: ${response.statusText}`);
    }

    return await response.json() as AgentInstance[];
    }
}
