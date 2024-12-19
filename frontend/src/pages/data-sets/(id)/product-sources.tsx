import { DataSetProductSourceList } from "@/components/DataSets/DataSetProductSourceList";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

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
