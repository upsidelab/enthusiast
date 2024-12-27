import { FormDescription, FormItem } from "@/components/ui/form.tsx";
import { UseFormReturn } from "react-hook-form";
import { DataSetListInput } from "@/components/util/data-set-list-input.tsx";
import { useEffect, useState } from "react";
import { DataSet } from "@/lib/types.ts";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const api = new ApiClient(authenticationProviderInstance);

export interface DataSetsFieldsProps {
  form: UseFormReturn<any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export function DataSetsFields({ form }: DataSetsFieldsProps) {
  const [availableDataSets, setAvailableDataSets] = useState<DataSet[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const result = await api.dataSets().getDataSets();
      setAvailableDataSets(result);
    };

    fetchData();
  }, []);

  return (
    <FormItem>
      <div className="mb-4">
        <h3 className="text-lg font-medium">Data Sets</h3>
        <FormDescription>Select the data sets that this account should have access to.</FormDescription>
      </div>
      <DataSetListInput name="dataSetIds" form={form} availableDataSets={availableDataSets} />
    </FormItem>
  );
}
