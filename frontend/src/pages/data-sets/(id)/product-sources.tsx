import { DataSetProductSourceList } from "@/components/data-sets/data-set-source-list";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function IndexDataSetCatalogSources() {
  const { id } = useParams();
  const dataSetId = Number(id);

  return (
    <PageMain>
      <PageHeading title="Manage Catalog Source Plugins" description="Add configuration details." />
      <DataSetProductSourceList dataSetId={dataSetId} />
    </PageMain>
  )
}
