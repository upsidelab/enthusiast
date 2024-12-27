import { ConfigureDataSetSourceForm } from "@/components/data-sets/configure-data-set-source-form.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { useParams } from 'react-router-dom';
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

export function ConfigureDataSetDocumentSource() {
  const { dataSetId, documentSourceId } = useParams<{ dataSetId: string; documentSourceId: string }>();
  const api = new ApiClient(authenticationProviderInstance);
  const getDataSetSource = api.dataSets().getDataSetDocumentSource.bind(api.dataSets());
  const configureDataSetSource = api.dataSets().configureDataSetDocumentSource.bind(api.dataSets());

  return (
    <PageMain>
      <PageHeading title="Configure Document Source Plugin" description="Add configuration details." />
      <ConfigureDataSetSourceForm 
        dataSetId={Number(dataSetId)} 
        sourceId={Number(documentSourceId)}
        getDataSetSource={getDataSetSource}
        configureDataSetSource={configureDataSetSource}
      />
    </PageMain>
  )
}
