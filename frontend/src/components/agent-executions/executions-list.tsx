import { useCallback, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Plus } from "lucide-react";
import { DEFAULT_PAGE_PARAM, PaginatedTable } from "@/components/util/paginated-table.tsx";
import { ExecutionStatusBadge } from "@/components/agent-executions/execution-status-badge.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { AgentExecution } from "@/lib/types.ts";

const api = new ApiClient(authenticationProviderInstance);

const STATUSES: AgentExecution["status"][] = ["pending", "in_progress", "finished", "failed"];
const STATUS_LABELS: Record<AgentExecution["status"], string> = {
  pending: "Pending",
  in_progress: "In progress",
  finished: "Finished",
  failed: "Failed",
};

export function ExecutionsList() {
  const { availableAgents, dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const agentId = searchParams.get("agent_id") ? Number(searchParams.get("agent_id")) : undefined;
  const status = searchParams.get("status") as AgentExecution["status"] | undefined ?? undefined;
  const hasActiveFilters = !!(agentId || status);

  const [hasItems, setHasItems] = useState(false);

  const agentName = (id: number) => availableAgents.find(a => a.id === id)?.name ?? `Agent #${id}`;

  const setFilter = (key: string, value: string | undefined) => {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev);
      if (value) next.set(key, value);
      else next.delete(key);
      next.delete(DEFAULT_PAGE_PARAM);
      return next;
    });
  };

  const loadItems = useCallback(
    async (page: number) => {
      const result = await api.agentExecutions().list({ datasetId: dataSetId ?? undefined, agentId, status }, page);
      setHasItems(result.count > 0);
      return result;
    },
    [dataSetId, agentId, status]
  );

  return (
    <div>
      <div className="flex items-center justify-end mb-4">
        <Button onClick={() => navigate(`/data-sets/${dataSetId}/agent-executions/new`)}>
          <Plus className="h-4 w-4" />New Execution
        </Button>
      </div>

      {(hasItems || hasActiveFilters) && <div className="flex gap-3 mb-6">
        <Select
          value={agentId?.toString() ?? "all"}
          onValueChange={v => setFilter("agent_id", v === "all" ? undefined : v)}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All agents" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All agents</SelectItem>
            {availableAgents.map(a => (
              <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={status ?? "all"}
          onValueChange={v => setFilter("status", v === "all" ? undefined : v)}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {STATUSES.map(s => (
              <SelectItem key={s} value={s}>{STATUS_LABELS[s]}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>}

      <PaginatedTable
        loadItems={loadItems}
        noItemsMessage={hasActiveFilters ? "No agent executions match your criteria" : "No agent executions created yet"}
        tableHeaders={["Status", "Agent", "Execution type", "Started", "Duration"]}
        tableHeaderWidths={["11%", "26%", "26%", "26%", "11%"]}
        tableRow={(item: AgentExecution, index) => (
          <TableRow
            key={index}
            onClick={() => navigate(`/data-sets/${dataSetId}/agent-executions/${item.id}`)}
            className="cursor-pointer"
          >
            <TableCell><ExecutionStatusBadge status={item.status} /></TableCell>
            <TableCell>{agentName(item.agent)}</TableCell>
            <TableCell className="font-mono text-sm">{item.execution_key}</TableCell>
            <TableCell>{new Date(item.started_at).toLocaleString("en-US")}</TableCell>
            <TableCell>
              {item.duration_seconds != null ? `${item.duration_seconds.toFixed(1)}s` : "—"}
            </TableCell>
          </TableRow>
        )}
      />
    </div>
  );
}
