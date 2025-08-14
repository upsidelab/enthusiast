import { DocumentsList } from "@/components/documents/documents-list.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";

export function DocumentsIndex() {
  return (
    <PageMain>
      <PageHeading title="Manage Documents" description="View documents synchronized from external systems." />
      <DocumentsList />
    </PageMain>
  );
}
