import { ReactNode, useState, useEffect, useRef } from "react";
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
  const [supportedFileExtensions, setSupportedFileExtensions] = useState<string[]>([]);
  const [isLoadingFileExtensions, setIsLoadingFileExtensions] = useState(true);
  const [fileExtensionsError, setFileExtensionsError] = useState<string | null>(null);
  const hasFetchedFileExtensions = useRef(false);
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

  const fetchAgentsForDataSet = async () => {
    if (!dataSetId) return;

    setIsLoadingAgents(true);
    try {
      const agents = await api.agents().getDatasetAvailableAgents(dataSetId);
      setAvailableAgents(agents.filter(agent => !agent.corrupted));
    } catch (error) {
      console.error("Failed to load agents:", error);
      setAvailableAgents([]);
    } finally {
      setIsLoadingAgents(false);
    }
  };

  useEffect(() => {
    fetchAgentsForDataSet();
  }, [dataSetId]);

  useEffect(() => {
    const fetchSupportedFileExtensions = async () => {
      if (hasFetchedFileExtensions.current) return;
      hasFetchedFileExtensions.current = true;

      try {
        const supportedTypes = await api.conversations().getSupportedFileTypes();
        setSupportedFileExtensions(supportedTypes.supported_extensions);
        setFileExtensionsError(null);
      } catch (error) {
        console.error('Failed to fetch supported file types:', error);
        setSupportedFileExtensions([]);
        setFileExtensionsError('Failed to load supported file types');
      } finally {
        setIsLoadingFileExtensions(false);
      }
    };

    fetchSupportedFileExtensions();
  }, []);

  const value: ApplicationContextValue = {
    dataSets,
    setDataSets,
    dataSetId,
    setDataSetId,
    availableAgents,
    setAvailableAgents,
    isLoadingAgents,
    setIsLoadingAgents,
    refetchAgents: fetchAgentsForDataSet,
    account,
    setAccount,
    supportedFileExtensions,
    setSupportedFileExtensions,
    isLoadingFileExtensions,
    setIsLoadingFileExtensions,
    fileExtensionsError,
    setFileExtensionsError
  };

  return (
    <ApplicationContext.Provider value={value}>
      {children}
    </ApplicationContext.Provider>
  );
}
