import { CreateService } from "@/components/ApiConnections/CreateServiceAccount.tsx";
import { PageHeading } from "@/components/util/PageHeading.tsx";
import { PageMain } from "@/components/util/PageMain.tsx";

export function CreateServiceAccount() {
  return (
    <PageMain>
      <PageHeading title="Create a New Service Account" description="Service accounts allows you to connect external systems." />      <CreateService/>
    </PageMain>
  );
}