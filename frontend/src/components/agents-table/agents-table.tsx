import { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useApplicationContext } from "@/lib/use-application-context";

import { DeleteConfirmationModal } from "./delete-confirmation-modal";
import { useAgents } from "./hooks/use-agents";
import { useAgentTypes } from "./hooks/use-agent-types";
import { Agent } from "@/lib/types";
import { AgentFormModal } from "./agent-form-modal";

export default function AgentsTable() {
  const { dataSetId } = useApplicationContext() ?? { dataSetId: null };
  const { agents, loadingAgents, refreshAgents } = useAgents(dataSetId);
  const { agentTypes, loadingTypes } = useAgentTypes();
  
  const [formModalOpen, setFormModalOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<Agent | null>(null);

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

  const handleFormSuccess = () => {
    setFormModalOpen(false);
    refreshAgents();
  };

  const handleFormClose = (open: boolean) => {
    if (!open) {
      setFormModalOpen(false);
      setEditingAgent(null);
    }
  };

  const handleDeleteSuccess = () => {
    setDeleteModalOpen(false);
    setAgentToDelete(null);
    refreshAgents();
  };

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <span className="text-lg font-semibold">Agents</span>
        <Button onClick={openNew}>New</Button>
      </div>
      
      {loadingAgents ? (
        <div>Loading agents...</div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {agents.map(agent => (
              <TableRow key={agent.id}>
                <TableCell>{agent.name}</TableCell>
                <TableCell>
                  {agentTypes.find(t => t.key === agent.agent_type)?.name || agent.agent_type || 'Unknown'}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => openEdit(agent)}>Edit</Button>
                    <Button size="sm" variant="destructive" onClick={() => handleDelete(agent)}>Delete</Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

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
