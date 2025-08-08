import { EditDataSetForm } from "@/components/data-sets/edit-data-set-form.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function EditDataSet() {
  return (
    <PageMain>
      <PageHeading title="Edit Data Set" description="Update your data set configuration." />
      <EditDataSetForm />
    </PageMain>
  )
} 
