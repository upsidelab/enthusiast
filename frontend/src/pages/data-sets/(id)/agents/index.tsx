import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import AgentsTable from "@/components/agents-table";

export default function AgentsPage() {
  return (
    <PageMain>
      <PageHeading title="Agents" description="Manage the agents for this dataset." />
      <AgentsTable />
    </PageMain>
  );
}
