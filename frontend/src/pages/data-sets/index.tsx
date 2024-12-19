import { DataSetList } from "@/components/data-sets/data-set-list.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function DataSetsIndex() {
  return (
    <PageMain>
      <PageHeading title="Manage Data Sets" description="Organize your products and documents with data sets." />
      <DataSetList />
    </PageMain>
  )
}
