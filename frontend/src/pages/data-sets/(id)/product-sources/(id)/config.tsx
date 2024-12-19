import { ConfigureProductSourceForm } from "@/components/DataSets/ConfigureProductSourceForm";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";
import { useParams } from 'react-router-dom';

export function ConfigureDataSetProductSource() {
  const { dataSetId, productSourceId } = useParams<{ dataSetId: string; productSourceId: string }>();

  return (
    <PageMain>
      <PageHeading title="Configure Product Source Plugin" description="Add configuration details." />
      <ConfigureProductSourceForm dataSetId={Number(dataSetId)} productSourceId={Number(productSourceId)} />
    </PageMain>
  )
}
