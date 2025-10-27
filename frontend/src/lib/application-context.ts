import { createContext } from "react";
import { Account, DataSet } from "@/lib/types.ts";

export interface ApplicationContextValue {
  dataSets: DataSet[];
  setDataSets: (dataSets: DataSet[]) => void;
  dataSetId: number | null;
  setDataSetId: (id: number | null) => void;
  availableAgents: { name: string; id: number; corrupted?: boolean; }[];
  setAvailableAgents: (agents: { name: string; id: number; corrupted?: boolean; }[]) => void;
  isLoadingAgents: boolean;
  setIsLoadingAgents: (value: boolean) => void;
  refetchAgents: () => Promise<void>;
  account: Account | null;
  setAccount: (account: Account | null) => void;
  supportedFileExtensions: string[];
  setSupportedFileExtensions: (extensions: string[]) => void;
  isLoadingFileExtensions: boolean;
  setIsLoadingFileExtensions: (value: boolean) => void;
  fileExtensionsError: string | null;
  setFileExtensionsError: (error: string | null) => void;
}

export const ApplicationContext = createContext<ApplicationContextValue | null>(null);
