import {BaseApiClient} from "@/lib/api/base.ts";

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
    async getAvailableAgents(): Promise<AgentChoice[]> {
        const response = await fetch(`${this.apiBase}/api/agents/types`, this._requestConfiguration());

        if (!response.ok) {
            throw new Error(`Failed to fetch available agents: ${response.statusText}`);
        }

        const result = await response.json() as AvailableAgentsResponse;
        return result.choices;
    }
}
