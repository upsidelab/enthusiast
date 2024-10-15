import { createContext } from "react";
import { Account } from "@/lib/api.ts";

export interface ApplicationContextValue {
  dataSetId: number | null;
  setDataSetId: (id: number | null) => void;
  account: Account | null;
  setAccount: (account: Account | null) => void;
}

export const ApplicationContext = createContext<ApplicationContextValue | null>(null);
