import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { FileIcon } from "lucide-react";
import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { ExecutionStatusBadge } from "@/components/agentic-executions/execution-status-badge.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { AgenticExecutionDetail } from "@/lib/types.ts";

const api = new ApiClient(authenticationProviderInstance);

const TERMINAL_STATUSES: AgenticExecutionDetail["status"][] = ["finished", "failed"];

export function AgenticExecutionDetailPage() {
  const { id: dataSetId, executionId } = useParams();
  const { availableAgents } = useApplicationContext()!;
  const [execution, setExecution] = useState<AgenticExecutionDetail | null>(null);

  const agentName = (id: number) => availableAgents.find(a => a.id === id)?.name ?? `Agent #${id}`;

  useEffect(() => {
    if (!executionId) return;

    let active = true;
    let interval: ReturnType<typeof setInterval> | null = null;

    const fetchExecution = async () => {
      const data = await api.agenticExecutions().get(Number(executionId));
      if (!active) return;
      setExecution(data);
      if (!TERMINAL_STATUSES.includes(data.status)) {
        interval = setInterval(async () => {
          const updated = await api.agenticExecutions().get(Number(executionId));
          if (!active) return;
          setExecution(updated);
          if (TERMINAL_STATUSES.includes(updated.status)) {
            clearInterval(interval!);
          }
        }, 3000);
      }
    };

    fetchExecution();

    return () => {
      active = false;
      if (interval) clearInterval(interval);
    };
  }, [executionId]);

  if (!execution) {
    return (
      <PageMain>
        <div className="text-muted-foreground text-sm">Loading...</div>
      </PageMain>
    );
  }

  const isRunning = !TERMINAL_STATUSES.includes(execution.status);

  return (
    <PageMain>
      <PageHeading
        title={execution.execution_key}
        description={`Agent: ${agentName(execution.agent)}`}
      >
        <div className="ml-auto flex items-center gap-3">
          <ExecutionStatusBadge status={execution.status} />
        </div>
      </PageHeading>

      <div className="space-y-6">
        <div className="flex gap-8 text-sm">
          <div>
            <p className="text-muted-foreground">Started</p>
            <p>{new Date(execution.started_at).toLocaleString("en-US")}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Duration</p>
            <p>{execution.duration_seconds != null ? `${execution.duration_seconds.toFixed(1)}s` : "—"}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Conversation</p>
            <Link
              to={`/data-sets/${dataSetId}/chat/${execution.conversation}`}
              className="text-primary underline-offset-4 hover:underline"
            >
              View conversation
            </Link>
          </div>
        </div>

        {isRunning && (
          <div className="text-sm text-muted-foreground animate-pulse">
            Running…
          </div>
        )}

        <div>
          <p className="text-sm font-medium mb-2">Input</p>
          <pre className="rounded-md bg-muted p-4 text-sm overflow-auto whitespace-pre-wrap">
            {JSON.stringify(execution.input, null, 2)}
          </pre>
        </div>

        {execution.files.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-2">Uploaded files</p>
            <ul className="space-y-1">
              {execution.files.map(file => (
                <li key={file.id} className="flex items-center gap-2 text-sm">
                  <FileIcon className="h-4 w-4 text-muted-foreground" />
                  {file.filename}
                </li>
              ))}
            </ul>
          </div>
        )}

        {execution.status === "finished" && execution.result && (
          <div>
            <p className="text-sm font-medium mb-2">Result</p>
            <pre className="rounded-md bg-muted p-4 text-sm overflow-auto whitespace-pre-wrap">
              {JSON.stringify(execution.result, null, 2)}
            </pre>
          </div>
        )}

        {execution.status === "failed" && (
          <div className="rounded-md border border-red-200 bg-red-50 p-4 space-y-2">
            {execution.failure_code && (
              <p className="text-sm">
                <span className="text-muted-foreground">Failure code: </span>
                <code className="font-mono">{execution.failure_code}</code>
              </p>
            )}
            {execution.failure_explanation && (
              <p className="text-sm text-red-700">{execution.failure_explanation}</p>
            )}
          </div>
        )}
      </div>
    </PageMain>
  );
}
