import { DataSetSourceList } from "@/components/data-sets/data-set-source-list.tsx";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function IndexDataSetIntegrations() {
  const { id } = useParams();
  const dataSetId = Number(id);

  return (
    <PageMain>
      <PageHeading title="Manage Integrations" description="Add and configure E-Commerce and CMS integrations." />
      <DataSetSourceList dataSetId={dataSetId} />
    </PageMain>
  )
} 
