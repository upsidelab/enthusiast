import { DataSetUserList } from "@/components/data-sets/data-set-user-list.tsx";
import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

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
