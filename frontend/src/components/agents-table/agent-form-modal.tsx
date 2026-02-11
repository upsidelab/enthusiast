import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Agent, AGENT_CONFIG_SECTION_KEYS, type AgentConfig, type AgentConfigSectionKey } from "@/lib/types";
import { useAgentForm } from "./hooks/use-agent-form";
import type { AgentChoice } from "@/lib/api/agents";
import { Textarea } from "@/components/ui/textarea";
import { FormModal } from "@/components/ui/form-modal";
import { useEffect } from "react";
import { RjsfForm } from "@/components/rjsf";

function useScrollToFirstError(fieldErrors: Record<string, string>) {
  useEffect(() => {
    if (Object.keys(fieldErrors).length === 0) return;
    const timer = setTimeout(() => {
      document.querySelector("[data-field-error]")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
    return () => clearTimeout(timer);
  }, [fieldErrors]);
}

const SECTION_TITLES: Record<AgentConfigSectionKey, string> = {
  agent_args: "Agent args",
  prompt_input: "Prompt input",
  prompt_extension: "Prompt extension",
};

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
    selectedType,
    updateConfigSection,
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

  useScrollToFirstError(fieldErrors);

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
      dependencies={[type, selectedType, config, openSections, generalError, fieldErrors]}
    >
      {generalError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-sm text-destructive">{generalError}</p>
        </div>
      )}

      <div className="flex flex-col gap-1" {...(fieldErrors.type ? { "data-field-error": "true" } : {})}>
        <Label htmlFor="agent-type">Type</Label>
        <Select value={type} onValueChange={setType} disabled={agentTypes.length === 0 || !!agent}>
          <SelectTrigger id="agent-type" className={fieldErrors.type ? "border-destructive" : ""}>
            <SelectValue placeholder="Select type"/>
          </SelectTrigger>
          <SelectContent>
            {agentTypes.map(t => (
              <SelectItem key={t.key} value={t.key}>{t.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {agentTypes.length === 0 &&
          <p className="text-[0.8rem] text-muted-foreground">First, you'll need to install an agent.<br /> To get started quickly, you can choose on of our <a href="https://upsidelab.io/tools/enthusiast/agents" className="underline">pre-built ones</a> to get started quick.</p>
        }
        {fieldErrors.type && (
          <p className="text-xs text-destructive">{fieldErrors.type}</p>
        )}
      </div>

      <div className="flex flex-col gap-1" {...(fieldErrors.name ? { "data-field-error": "true" } : {})}>
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

      <div className="flex flex-col gap-1" {...(fieldErrors.description ? { "data-field-error": "true" } : {})}>
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

      {type && selectedType && (
        <RjsfForm
          choice={selectedType}
          config={config}
          sectionKeys={AGENT_CONFIG_SECTION_KEYS}
          sectionTitles={SECTION_TITLES}
          onConfigChange={(key, value) => updateConfigSection(key as keyof AgentConfig, value)}
          fieldErrors={fieldErrors}
          openSections={openSections}
          onOpenSectionsChange={setOpenSections}
          header={
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-foreground">Configuration</h4>
              <p className="text-xs text-muted-foreground">Configure agent parameters</p>
            </div>
          }
          emptyMessage={
            <>
              <p className="text-sm text-muted-foreground mb-2">No configuration required</p>
              <p className="text-xs text-muted-foreground">
                This agent type doesn't require any additional configuration parameters.
              </p>
            </>
          }
        />
      )}
    </FormModal>
  );
}
