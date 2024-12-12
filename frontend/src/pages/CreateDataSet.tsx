import { CreateDataSetForm } from "@/components/DataSets/CreateDataSetForm.tsx";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

export default function CreateDataSet() {
  return (
    <PageMain>
      <PageHeading title="Create Data Set" description="Data sets allow you to organize products and documents." />
      <CreateDataSetForm/>
    </PageMain>
  )
}
