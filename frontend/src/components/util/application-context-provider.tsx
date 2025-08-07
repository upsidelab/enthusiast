import { ReactNode, useState, useEffect } from "react";
import { ApplicationContext, ApplicationContextValue } from "@/lib/application-context.ts";
import { Account, DataSet } from "@/lib/types.ts";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useLocation, useNavigate } from "react-router-dom";

const api = new ApiClient(authenticationProviderInstance);

export interface ApplicationContextProviderProps {
  children: ReactNode;
}

function extractDataSetIdFromPath(path: string): number | null {
  const match = path.match(/\/data-sets\/(\d+)/);
  return match ? parseInt(match[1]) : null;
}

function buildNewUrl(path: string, newDataSetId: number): string {
  const pathParts = path.split("/data-sets/");
  const dataSetPath = pathParts[1] || "";
  const pathSegments = dataSetPath.split("/");
  const remainingPath = pathSegments.slice(1).join("/") || "";
  return `/data-sets/${newDataSetId}/${remainingPath}`;
}

export function ApplicationContextProvider({ children }: ApplicationContextProviderProps) {
  const [dataSets, setDataSets] = useState<DataSet[]>([]);
  const [dataSetId, setDataSetId] = useState<number | null>(null);
  const [availableAgents, setAvailableAgents] = useState<{ name: string; id: number; }[]>([]);
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [account, setAccount] = useState<Account | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDataSets = async () => {
      const apiDataSets = await api.dataSets().getDataSets();
      setDataSets(apiDataSets);

      if (location.pathname.includes("/data-sets/") && !location.pathname.endsWith("/data-sets/new")) {
        const urlDataSetId = extractDataSetIdFromPath(location.pathname);

        if (apiDataSets.length > 0) {
          if (urlDataSetId && apiDataSets.some(ds => ds.id === urlDataSetId)) {
            setDataSetId(urlDataSetId);
          } else {
            const defaultId = apiDataSets[0].id!;
            setDataSetId(defaultId);
            const newUrl = buildNewUrl(location.pathname, defaultId);
            navigate(newUrl, { replace: true });
          }
        }
      }
    };

    fetchDataSets();
  }, [location.pathname, navigate]);

  useEffect(() => {
  const fetchAgentsForDataSet = async () => {
    if (!dataSetId) return;

    setIsLoadingAgents(true);
    try {
      const instances = await api.agents().getDatasetAvailableAgents(dataSetId);
      setAvailableAgents(instances);
    } catch (error) {
      console.error("Failed to load agent instances:", error);
      setAvailableAgents([]);
    } finally {
      setIsLoadingAgents(false);
    }
  };

  fetchAgentsForDataSet();
}, [dataSetId]);

  const value: ApplicationContextValue = {
    dataSets,
    setDataSets,
    dataSetId,
    setDataSetId,
    availableAgents,
    setAvailableAgents,
    isLoadingAgents,
    setIsLoadingAgents,
    account,
    setAccount
  };

  return (
    <ApplicationContext.Provider value={value}>
      {children}
    </ApplicationContext.Provider>
  );
}
