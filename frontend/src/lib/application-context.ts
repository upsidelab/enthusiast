import { createContext } from "react";
import { Account, DataSet } from "@/lib/types.ts";

export interface ApplicationContextValue {
  dataSets: DataSet[];
  setDataSets: (dataSets: DataSet[]) => void;
  dataSetId: number | null;
  setDataSetId: (id: number | null) => void;
  availableAgentInstances: { name: string; id: number; }[];
  setAvailableAgentInstances: (agents: { name: string; id: number; }[]) => void;
  isLoadingAgents: boolean;
  setIsLoadingAgents: (value: boolean) => void;
  account: Account | null;
  setAccount: (account: Account | null) => void;
}

export const ApplicationContext = createContext<ApplicationContextValue | null>(null);
