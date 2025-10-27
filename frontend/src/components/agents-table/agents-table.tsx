import { useState } from "react";
import { TableCell, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useApplicationContext } from "@/lib/use-application-context";
import { AlertTriangle, Plus, Settings, Trash2 } from "lucide-react";

import { DeleteConfirmationModal } from "./delete-confirmation-modal";
import { useAgentTypes } from "./hooks/use-agent-types";
import { Agent, PaginatedResult } from "@/lib/types";
import { AgentFormModal } from "./agent-form-modal";
import { PaginatedTable } from "@/components/util/paginated-table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ButtonWithTooltip } from "@/components/ui/button-with-tooltip.tsx";

const api = new ApiClient(authenticationProviderInstance);

export default function AgentsTable() {
  const { dataSetId, refetchAgents } = useApplicationContext() ?? { dataSetId: null, refetchAgents: async () => {} };
  const { agentTypes, loadingTypes } = useAgentTypes();
  
  const [formModalOpen, setFormModalOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<Agent | null>(null);

  const fetchAgents = async (): Promise<PaginatedResult<Agent> | undefined> => {
    if (dataSetId === null) {
      return;
    }

    const agents = await api.agents().getDatasetAvailableAgents(dataSetId);
    return {
      results: agents,
      count: agents.length
    };
  }

  const openNew = () => {
    setEditingAgent(null);
    setFormModalOpen(true);
  };

  const openEdit = (agent: Agent) => {
    setEditingAgent(agent);
    setFormModalOpen(true);
  };

  const handleDelete = (agent: Agent) => {
    setAgentToDelete(agent);
    setDeleteModalOpen(true);
  };

  const handleFormSuccess = async () => {
    setFormModalOpen(false);
    await refetchAgents();
  };

  const handleFormClose = (open: boolean) => {
    if (!open) {
      setFormModalOpen(false);
      setEditingAgent(null);
    }
  };

  const handleDeleteSuccess = async () => {
    setDeleteModalOpen(false);
    setAgentToDelete(null);
    await refetchAgents();
  };

  return (
    <>
      <div className="flex items-center justify-end mb-6">
        <Button onClick={openNew}><Plus className="h-4 w-4"/>New agent</Button>
      </div>

      <PaginatedTable
        loadItems={fetchAgents}
        itemsReloadDependencies={1}
        noItemsMessage="You haven't configured any agents yet"
        tableHeaders={["Name", "Type", "Action"]}
        tableRow={(item, index) => {
          return (<TableRow key={index}>
            <TableCell>
              <div className="flex items-center gap-2">
                {item.corrupted && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                <span className={item.corrupted ? "text-muted-foreground" : ""}>
                    {item.name}
                  </span>
              </div>
            </TableCell>
            <TableCell className={"w-1/4"}>
              {agentTypes.find(t => t.key === item.agent_type)?.name || item.agent_type || 'Unknown'}
            </TableCell>
            <TableCell className="text-right w-1">
              <div className="flex justify-end space-x-2">
                <ButtonWithTooltip
                  variant="outline"
                  size="sm"
                  onClick={() => openEdit(item)}
                  tooltip="Settings"
                >
                  <Settings className="h-4 w-4"/>
                </ButtonWithTooltip>
                <ButtonWithTooltip
                  variant="outline"
                  size="sm"
                  onClick={() => handleDelete(item)}
                  tooltip="Delete"
                >
                  <Trash2 className="h-4 w-4"/>
                </ButtonWithTooltip>
              </div>
            </TableCell>
          </TableRow>)
        }}
      />

      <AgentFormModal
        open={formModalOpen}
        onOpenChange={handleFormClose}
        agent={editingAgent}
        agentTypes={agentTypes}
        loadingTypes={loadingTypes}
        dataSetId={dataSetId}
        onSuccess={handleFormSuccess}
      />

      <DeleteConfirmationModal
        open={deleteModalOpen}
        onOpenChange={setDeleteModalOpen}
        agent={agentToDelete}
        onConfirm={handleDeleteSuccess}
      />
    </>
  );
}
