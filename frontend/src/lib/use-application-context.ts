import { useContext } from "react";
import { ApplicationContext } from "@/lib/application-context.ts";

export function useApplicationContext() {
  return useContext(ApplicationContext);
}
