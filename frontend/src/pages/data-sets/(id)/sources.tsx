import { DataSetSourceList } from "@/components/data-sets/data-set-source-list.tsx";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function IndexDataSetSources() {
  const { id } = useParams();
  const dataSetId = Number(id);

  return (
    <PageMain>
      <PageHeading title="Manage Sources" description="Add and configure product and document sources." />
      <DataSetSourceList dataSetId={dataSetId} />
    </PageMain>
  )
} 
