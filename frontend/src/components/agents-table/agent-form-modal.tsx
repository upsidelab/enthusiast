import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Agent } from "@/lib/types";
import { useAgentForm } from "./hooks/use-agent-form";
import { AgentConfigurationForm } from "./agent-configuration-form";
import {AgentChoice} from "@/lib/api/agents.ts";
import {Textarea} from "@/components/ui/textarea.tsx";
import { FormModal } from "@/components/ui/form-modal";
import { useEffect } from "react";

interface AgentFormModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  agent: Agent | null;
  agentTypes: AgentChoice[];
  loadingTypes: boolean;
  dataSetId: number | null;
  onSuccess: () => void;
}

export function AgentFormModal({
  open,
  onOpenChange,
  agent,
  agentTypes,
  loadingTypes,
  dataSetId,
  onSuccess
}: AgentFormModalProps) {
  const {
    name,
    setName,
    description,
    setDescription,
    type,
    setType,
    config,
    setConfig,
    agentConfigSections,
    openSections,
    setOpenSections,
    fieldErrors,
    generalError,
    submitting,
    handleSubmit,
    resetForm
  } = useAgentForm(agent, agentTypes, dataSetId, onSuccess);

  // Reset form when modal closes
  useEffect(() => {
    if (!open) {
      resetForm();
    }
  }, [open, resetForm]);

  const onSubmit = async () => {
    await handleSubmit();
  };

  const isEditing = !!agent;
  const title = isEditing ? `Edit Agent` : `New Agent`;

  return (
    <FormModal
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      onSubmit={onSubmit}
      onCancel={() => onOpenChange(false)}
      submitLabel={isEditing ? "Save" : "Create"}
      submitting={submitting}
      disabled={!name || !type}
      loading={loadingTypes}
      loadingText="Loading agent types..."
      dependencies={[type, agentConfigSections, openSections, generalError, fieldErrors]}
    >
      {generalError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-sm text-destructive">{generalError}</p>
        </div>
      )}
      
      <div className="flex flex-col gap-1">
        <Label htmlFor="agent-name">Name</Label>
        <Input 
          id="agent-name" 
          placeholder="Name" 
          value={name} 
          onChange={e => setName(e.target.value)}
          className={fieldErrors.name ? "border-destructive" : ""}
        />
        {fieldErrors.name && (
          <p className="text-xs text-destructive">{fieldErrors.name}</p>
        )}
      </div>
      
      <div className="flex flex-col gap-1">
        <Label htmlFor="agent-description">Description</Label>
        <Textarea
          id="agent-description" 
          placeholder="Description"
          value={description} 
          onChange={e => setDescription(e.target.value)}
        />
        {fieldErrors.description && (
          <p className="text-xs text-destructive">{fieldErrors.description}</p>
        )}
      </div>
      
      <div className="flex flex-col gap-1">
        <Label htmlFor="agent-type">Type</Label>
        <Select value={type} onValueChange={setType}>
          <SelectTrigger id="agent-type" className={fieldErrors.type ? "border-destructive" : ""}>
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            {agentTypes.map(t => (
              <SelectItem key={t.key} value={t.key}>{t.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {fieldErrors.type && (
          <p className="text-xs text-destructive">{fieldErrors.type}</p>
        )}
      </div>
      
      {type && (
        <AgentConfigurationForm
          agentConfigSections={agentConfigSections}
          openSections={openSections}
          setOpenSections={setOpenSections}
          config={config}
          setConfig={setConfig}
          fieldErrors={fieldErrors}
        />
      )}
    </FormModal>
  );
}
