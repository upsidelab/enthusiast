import { AgentExecution } from "@/lib/types.ts";
import { cn } from "@/lib/utils.ts";

const STATUS_STYLES: Record<AgentExecution["status"], string> = {
  pending: "bg-muted text-muted-foreground",
  in_progress: "bg-blue-100 text-blue-700",
  finished: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

const STATUS_LABELS: Record<AgentExecution["status"], string> = {
  pending: "Pending",
  in_progress: "In progress",
  finished: "Finished",
  failed: "Failed",
};

interface ExecutionStatusBadgeProps {
  status: AgentExecution["status"];
}

export function ExecutionStatusBadge({ status }: ExecutionStatusBadgeProps) {
  return (
    <span className={cn("inline-flex items-center rounded-md px-2 py-1 text-xs font-medium", STATUS_STYLES[status])}>
      {STATUS_LABELS[status]}
    </span>
  );
}
