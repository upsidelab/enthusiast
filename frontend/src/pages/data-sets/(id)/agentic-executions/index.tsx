import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { ExecutionsList } from "@/components/agentic-executions/executions-list.tsx";

export function AgenticExecutionsPage() {
  return (
    <PageMain>
      <PageHeading
        title="Agentic Executions"
        description="Track autonomous agentic execution jobs and inspect their results."
      />
      <ExecutionsList />
    </PageMain>
  );
}
