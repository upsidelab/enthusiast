import { ReactNode, useState, useEffect } from "react";
import { ApplicationContext, ApplicationContextValue } from "@/lib/application-context.ts";
import { Account, DataSet } from "@/lib/types.ts";

export interface ApplicationContextProviderProps {
  children: ReactNode;
}

export function ApplicationContextProvider({ children }: ApplicationContextProviderProps) {
  const [dataSets, setDataSets] = useState<DataSet[]>([]);
  const [dataSetId, setDataSetId] = useState<number | null>(() => {
  const storedDataSetId = sessionStorage.getItem('selectedDataSetId');
  return storedDataSetId ? parseInt(storedDataSetId) : null;
  });
  const [account, setAccount] = useState<Account | null>(null);

  useEffect(() => {
    if (dataSetId !== null) {
      sessionStorage.setItem('selectedDataSetId', dataSetId.toString());
    } else {
      sessionStorage.removeItem('selectedDataSetId');
    }
  }, [dataSetId]);

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
