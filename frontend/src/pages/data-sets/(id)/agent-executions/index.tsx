import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { ExecutionsList } from "@/components/agent-executions/executions-list.tsx";

export function AgentExecutionsPage() {
  return (
    <PageMain>
      <PageHeading
        title="Agent Executions"
        description="Track autonomous agent execution jobs and inspect their results."
      />
      <ExecutionsList />
    </PageMain>
  );
}
