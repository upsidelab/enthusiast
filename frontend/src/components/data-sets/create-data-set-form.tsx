import { useNavigate } from "react-router-dom";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { DataSet } from "@/lib/types.ts";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { DataSetForm } from "./data-set-form.tsx";
import { DataSetFormSchema } from "./data-set-form-schema.ts";

const api = new ApiClient(authenticationProviderInstance);

export interface CreateDataSetFormProps {
  isOnboarding?: boolean;
}

export function CreateDataSetForm({ isOnboarding = false }: CreateDataSetFormProps) {
  const {setDataSets, setDataSetId} = useApplicationContext()!;
  const navigate = useNavigate();

  const submitLabel = isOnboarding ? "Continue" : "Create"

  const handleSubmit = async (values: DataSetFormSchema) => {
    const createdDataSetId = await api.dataSets().createDataSet({ ...values, id: undefined } as DataSet);
    const dataSets = await api.dataSets().getDataSets();
    setDataSets(dataSets);
    setDataSetId(createdDataSetId);
    navigate(`/data-sets/${createdDataSetId}/integrations`);
  };

  return (
    <DataSetForm
      onSubmit={handleSubmit}
      isOnboarding={isOnboarding}
      submitButtonText={submitLabel}
    />
  );
}
