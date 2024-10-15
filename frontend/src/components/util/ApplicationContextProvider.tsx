import { ReactNode, useState } from "react";
import { ApplicationContext, ApplicationContextValue } from "@/lib/application-context.ts";
import { Account } from "@/lib/api.ts";

export interface ApplicationContextProviderProps {
  children: ReactNode;
}

export function ApplicationContextProvider({ children }: ApplicationContextProviderProps) {
  const [dataSetId, setDataSetId] = useState<number | null>(null);
  const [account, setAccount] = useState<Account | null>(null);

  const value: ApplicationContextValue = {
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
