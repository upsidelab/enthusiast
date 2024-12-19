import { CreateService } from "@/components/api-connections/create-service-account.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function ApiConnectionNew() {
  return (
    <PageMain>
      <PageHeading title="Create a New Service Account" description="Service accounts allows you to connect external systems." />      <CreateService/>
    </PageMain>
  );
}
