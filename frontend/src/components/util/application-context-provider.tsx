import { ReactNode, useState, useEffect } from "react";
import { ApplicationContext, ApplicationContextValue } from "@/lib/application-context.ts";
import { Account, DataSet } from "@/lib/types.ts";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const api = new ApiClient(authenticationProviderInstance);

export interface ApplicationContextProviderProps {
  children: ReactNode;
}

export function ApplicationContextProvider({ children }: ApplicationContextProviderProps) {
  const [dataSets, setDataSets] = useState<DataSet[]>([]);
  const [dataSetId, setDataSetId] = useState<number | null>(null);
  const [account, setAccount] = useState<Account | null>(null);

  useEffect(() => {
    const fetchDataSets = async () => {
      const apiDataSets = await api.dataSets().getDataSets();
      setDataSets(apiDataSets);
      if (apiDataSets.length > 0) {
        setDataSetId(apiDataSets[0].id);
      }
    };

    fetchDataSets();
  }, []);

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
