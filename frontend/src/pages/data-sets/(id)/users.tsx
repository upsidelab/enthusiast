import { DataSetUserList } from "@/components/DataSets/DataSetUserList.tsx";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

export function IndexDataSetUsers() {
  const {id} = useParams();
  const dataSetId = Number(id);

  return (
    <PageMain>
      <PageHeading title="Manage Data Set Access"
                   description="Control access to data sets by selecting users and applications."/>
      <DataSetUserList dataSetId={dataSetId}/>
    </PageMain>
  )
}
