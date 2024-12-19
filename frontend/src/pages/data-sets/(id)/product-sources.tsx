import { DataSetProductSourceList } from "@/components/data-sets/data-set-product-source-list.tsx";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function IndexDataSetProductSources() {
  const { id } = useParams();
  const dataSetId = Number(id);

  return (
    <PageMain>
      <PageHeading title="Manage Product Source Plugins" description="Add configuration details." />
      <DataSetProductSourceList dataSetId={dataSetId} />
    </PageMain>
  )
}
