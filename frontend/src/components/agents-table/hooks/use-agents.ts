import { useState, useEffect } from "react";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { Agent } from "@/lib/types";

const apiClient = new ApiClient(authenticationProviderInstance);

export function useAgents(dataSetId: number | null) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loadingAgents, setLoadingAgents] = useState(false);

  const fetchAgents = async () => {
    if (!dataSetId) return;
    
    setLoadingAgents(true);
    try {
      const fetchedAgents = await apiClient.agents().getDatasetAvailableAgents(dataSetId);
      setAgents(fetchedAgents);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoadingAgents(false);
    }
  };

  useEffect(() => {
    const loadAgentsForDataset = () => {
      fetchAgents();
    };

    loadAgentsForDataset();
  }, [dataSetId]);

  return {
    agents,
    loadingAgents,
    refreshAgents: fetchAgents
  };
}
