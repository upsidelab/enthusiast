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

export function ApplicationContextProvider({ children }: ApplicationContextProviderProps) {
  const [dataSets, setDataSets] = useState<DataSet[]>([]);
  const [dataSetId, setDataSetId] = useState<number | null>(null);
  const [account, setAccount] = useState<Account | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDataSets = async () => {
      const apiDataSets = await api.dataSets().getDataSets();
      setDataSets(apiDataSets);

      if (location.pathname.includes("/data-sets/")) {
        const urlDataSetId = parseInt(location.pathname.split("/data-sets/")[1]?.split("/")[0]);

        if (apiDataSets.length > 0) {
          if (urlDataSetId && apiDataSets.some(ds => ds.id === urlDataSetId)) {
            setDataSetId(urlDataSetId);
          } else {
            const defaultId = apiDataSets[0].id!;
            setDataSetId(defaultId);
            navigate(`/data-sets/${defaultId}${location.pathname.split("/data-sets/")[1]?.split("/").slice(1).join("/") || ""}`, { replace: true });
          }
        }
      }
    };

    fetchDataSets();
  }, [location.pathname, navigate]);

  const value: ApplicationContextValue = {
    dataSets,
    setDataSets,
    dataSetId,
    setDataSetId,
    account,
    setAccount
  };

  return (
    <ApplicationContext.Provider value={value}>
      {children}
    </ApplicationContext.Provider>
  );
}
