import { CreateDataSetForm } from "@/components/DataSets/CreateDataSetForm.tsx";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

export default function NewDataSet() {
  return (
    <PageMain>
      <PageHeading title="Create Data Set" description="Organize your products and documents with data sets." />
      <CreateDataSetForm/>
    </PageMain>
  )
}
