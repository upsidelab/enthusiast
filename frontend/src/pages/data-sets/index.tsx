import { DataSetList } from "@/components/DataSets/DataSetList.tsx";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

export function DataSetsIndex() {
  return (
    <PageMain>
      <PageHeading title="Manage Data Sets" description="Organize your products and documents with data sets." />
      <DataSetList />
    </PageMain>
  )
}
