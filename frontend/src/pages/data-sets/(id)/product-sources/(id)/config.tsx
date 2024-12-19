import { ConfigureProductSourceForm } from "@/components/data-sets/configure-product-source-form.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
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
