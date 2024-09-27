import { ReactNode, useState } from "react";
import { ApplicationContext, ApplicationContextValue } from "@/lib/application-context.ts";

export interface ApplicationContextProviderProps {
  children: ReactNode;
}

export function ApplicationContextProvider({ children }: ApplicationContextProviderProps) {
  const [dataSetId, setDataSetId] = useState<number | null>(null);

  const value: ApplicationContextValue = {
    dataSetId,
    setDataSetId
  };

  return (
    <ApplicationContext.Provider value={value}>
      {children}
    </ApplicationContext.Provider>
  );
}
