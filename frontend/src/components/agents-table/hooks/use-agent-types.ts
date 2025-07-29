import { useState, useEffect } from "react";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";

const apiClient = new ApiClient(authenticationProviderInstance);

export function useAgentTypes() {
  const [agentTypes, setAgentTypes] = useState<any[]>([]);
  const [loadingTypes, setLoadingTypes] = useState(true);

  useEffect(() => {
    const fetchAgentTypes = async () => {
      setLoadingTypes(true);
      try {
        const types = await apiClient.agents().getAvailableAgentTypes();
        setAgentTypes(types);
      } catch (error) {
        console.error('Failed to fetch agent types:', error);
      } finally {
        setLoadingTypes(false);
      }
    };

    fetchAgentTypes();
  }, []);

  return {
    agentTypes,
    loadingTypes
  };
}
