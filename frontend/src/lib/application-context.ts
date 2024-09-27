import { createContext } from "react";

export interface ApplicationContextValue {
  dataSetId: number | null;
  setDataSetId: (id: number | null) => void;
}

export const ApplicationContext = createContext<ApplicationContextValue | null>(null);
