import { DataSetList } from "@/components/DataSets/DataSetList.tsx";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

export function ManageDataSets() {
  return (
    <PageMain>
      <PageHeading title="Manage Data Sets" description="Data sets allow you to organize products and documents." />
      <DataSetList />
    </PageMain>
  )
}
