import { useNavigate, useParams } from "react-router-dom";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { DataSet } from "@/lib/types.ts";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { DataSetForm } from "./data-set-form.tsx";
import { useEffect, useState } from "react";
import { Spinner } from "@/components/util/spinner.tsx";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function EditDataSetForm() {
  const { setDataSets } = useApplicationContext()!;
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dataSet, setDataSet] = useState<DataSet | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch the actual data set
  useEffect(() => {
    const fetchDataSet = async () => {
      if (!id) {
        setError("No data set ID provided");
        setIsLoading(false);
        return;
      }

      try {
        const fetchedDataSet = await api.dataSets().getDataSet(parseInt(id));
        setDataSet(fetchedDataSet);
      } catch (err) {
        console.error("Error fetching data set:", err);
        setError("Failed to load data set");
      } finally {
        console.log(dataSet)
        setIsLoading(false);
      }
    };

    fetchDataSet();
  }, [id]);

  const handleSubmit = async (values: any) => {
    if (!id || !dataSet) {
      console.error("No data set ID or data available");
      return;
    }

    try {
      // Create the updated data set object
      const updatedDataSet: DataSet = {
        ...dataSet,
        ...values
      };

      // Call the API to update the data set
      await api.dataSets().updateDataSet(parseInt(id), updatedDataSet);
      
      // Refresh the data sets list
      const updatedDataSets = await api.dataSets().getDataSets();
      setDataSets(updatedDataSets);
      
      // Navigate back to the data sets list
      navigate('/data-sets');
    } catch (err) {
      console.error("Error updating data set:", err);
      setError("Failed to update data set");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Spinner />
        <span className="ml-2">Loading data set...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert>
        <AlertDescription>Error: {error}</AlertDescription>
      </Alert>
    );
  }

  if (!dataSet) {
    return (
      <Alert>
        <AlertDescription>Data set not found</AlertDescription>
      </Alert>
    );
  }

  return (
    <DataSetForm
      initialData={dataSet}
      onSubmit={handleSubmit}
      submitButtonText="Update"
    />
  );
} 
