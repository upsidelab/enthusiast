import { DataSetUserList } from "@/components/DataSets/DataSetUserList.tsx";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

export function ManageDataSetUsers() {
  const { id } = useParams();
  const dataSetId = Number(id);

  return (
    <PageMain>
      <PageHeading title="Manage Data Set Access" description="Choose which users and application can access data set." />
      <DataSetUserList dataSetId={dataSetId} />
    </PageMain>
  )
}
