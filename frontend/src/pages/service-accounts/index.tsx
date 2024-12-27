import { ServiceAccountsList } from "@/components/service-accounts/service-accounts-list.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";

export function ApiConnectionIndex() {
  return (
    <PageMain>
      <PageHeading title="Manage Service Accounts" description="Create service accounts to control programatic access to data sets" />
      <ServiceAccountsList />
    </PageMain>
  );
}
