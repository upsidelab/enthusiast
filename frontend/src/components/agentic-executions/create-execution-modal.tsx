import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FormModal } from "@/components/ui/form-modal";
import { JSONEditor } from "@/components/agents-table/json-editor";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { AgentDetails, ExecutionDefinition } from "@/lib/types.ts";
import { ApiError } from "@/lib/api-error.ts";

const api = new ApiClient(authenticationProviderInstance);

interface CreateExecutionModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateExecutionModal({ open, onOpenChange }: CreateExecutionModalProps) {
  const { availableAgents, dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();

  const [agentId, setAgentId] = useState<string>("");
  const [executionKey, setExecutionKey] = useState<string>("");
  const [inputJson, setInputJson] = useState<string>("{}");
  const [files, setFiles] = useState<File[]>([]);

  const [executionDefinitions, setExecutionDefinitions] = useState<ExecutionDefinition[]>([]);
  const [agentDetails, setAgentDetails] = useState<AgentDetails | null>(null);
  const [loadingDefinitions, setLoadingDefinitions] = useState(false);

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [inputValidationErrors, setInputValidationErrors] = useState<{ field: string; message: string }[]>([]);
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (!agentId) {
      setExecutionDefinitions([]);
      setAgentDetails(null);
      setExecutionKey("");
      return;
    }
    setFieldErrors({});
    setInputValidationErrors([]);
    setGeneralError(null);
    setLoadingDefinitions(true);
    setExecutionKey("");
    Promise.all([
      api.agenticExecutions().getDefinitions(Number(agentId)),
      api.agents().getAgentById(Number(agentId)),
    ])
      .then(([definitions, details]) => {
        setExecutionDefinitions(definitions);
        setAgentDetails(details);
      })
      .catch(() => {
        setExecutionDefinitions([]);
        setAgentDetails(null);
      })
      .finally(() => setLoadingDefinitions(false));
  }, [agentId]);

  const resetForm = () => {
    setAgentId("");
    setExecutionKey("");
    setInputJson("{}");
    setFiles([]);
    setExecutionDefinitions([]);
    setAgentDetails(null);
    setFieldErrors({});
    setInputValidationErrors([]);
    setGeneralError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  useEffect(() => {
    if (!open) resetForm();
  }, [open]);

  const handleSubmit = async () => {
    const errors: Record<string, string> = {};

    if (!agentId) errors.agent = "Please select an agent.";
    if (!executionKey) errors.execution_key = "Please select an execution definition.";

    let parsedInput: Record<string, unknown> = {};
    try {
      parsedInput = JSON.parse(inputJson);
      if (typeof parsedInput !== "object" || Array.isArray(parsedInput) || parsedInput === null) {
        errors.input = "Input must be a JSON object.";
      }
    } catch {
      errors.input = "Input is not valid JSON.";
    }

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }

    setFieldErrors({});
    setInputValidationErrors([]);
    setGeneralError(null);
    setSubmitting(true);

    try {
      const execution = await api.agenticExecutions().create(Number(agentId), {
        execution_key: executionKey,
        input: parsedInput,
        files: files.length > 0 ? files : undefined,
      });
      onOpenChange(false);
      navigate(`/data-sets/${dataSetId}/agentic-executions/${execution.id}`);
    } catch (err) {
      if (err instanceof ApiError) {
        const data = err.response.data as Record<string, unknown>;
        const newFieldErrors: Record<string, string> = {};
        let hasFieldErrors = false;

        for (const key of ["agent", "execution_key", "files"]) {
          if (Array.isArray(data[key])) {
            newFieldErrors[key] = (data[key] as string[]).join(" ");
            hasFieldErrors = true;
          }
        }

        if (data.input && typeof data.input === "object" && !Array.isArray(data.input)) {
          const entries = Object.entries(data.input as Record<string, string>).map(([field, message]) => ({ field, message }));
          if (entries.length > 0) {
            setInputValidationErrors(entries);
            hasFieldErrors = true;
          }
        } else if (Array.isArray(data.input)) {
          newFieldErrors.input = (data.input as string[]).join(" ");
          hasFieldErrors = true;
        }

        if (hasFieldErrors) {
          setFieldErrors(newFieldErrors);
        } else {
          const detail = typeof data.detail === "string" ? data.detail : null;
          const nonFieldErrors = Array.isArray(data.non_field_errors)
            ? (data.non_field_errors as string[]).join(" ")
            : null;
          setGeneralError(detail ?? nonFieldErrors ?? "Something went wrong. Please try again.");
        }
      } else {
        setGeneralError("Something went wrong. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleExecutionKeyChange = (key: string) => {
    setExecutionKey(key);
    setFieldErrors({});
    setInputValidationErrors([]);
    setGeneralError(null);
  };

  const canSubmit = !!agentId && !!executionKey && !loadingDefinitions;
  const supportsFiles = agentDetails?.file_upload === true && executionDefinitions.length > 0;
  const selectedDefinition = executionDefinitions.find(d => d.key === executionKey);

  return (
    <FormModal
      open={open}
      onOpenChange={onOpenChange}
      title="New Agentic Execution"
      onSubmit={handleSubmit}
      onCancel={() => onOpenChange(false)}
      submitLabel="Start"
      submitting={submitting}
      disabled={!canSubmit}
      dependencies={[agentId, executionKey, executionDefinitions, agentDetails, generalError, fieldErrors]}
    >
      {generalError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-sm text-destructive">{generalError}</p>
        </div>
      )}

      <div className="flex flex-col gap-1">
        <Label htmlFor="exec-agent">Agent</Label>
        <Select value={agentId} onValueChange={setAgentId} disabled={availableAgents.length === 0}>
          <SelectTrigger id="exec-agent" className={fieldErrors.agent ? "border-destructive" : ""}>
            <SelectValue placeholder="Select agent" />
          </SelectTrigger>
          <SelectContent>
            {availableAgents.map(a => (
              <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {fieldErrors.agent && <p className="text-xs text-destructive">{fieldErrors.agent}</p>}
      </div>

      <div className="flex flex-col gap-1">
        <Label htmlFor="exec-definition">Execution definition</Label>
        <Select
          value={executionKey}
          onValueChange={handleExecutionKeyChange}
          disabled={!agentId || loadingDefinitions || executionDefinitions.length === 0}
        >
          <SelectTrigger id="exec-definition" className={fieldErrors.execution_key ? "border-destructive" : ""}>
            <SelectValue placeholder={loadingDefinitions ? "Loading..." : "Select execution definition"} />
          </SelectTrigger>
          <SelectContent>
            {executionDefinitions.map(d => (
              <SelectItem key={d.key} value={d.key}>{d.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {agentId && !loadingDefinitions && executionDefinitions.length === 0 && (
          <p className="text-xs text-muted-foreground">No execution definitions available for this agent.</p>
        )}
        {selectedDefinition?.description && (
          <p className="text-xs text-muted-foreground">{selectedDefinition.description}</p>
        )}
        {fieldErrors.execution_key && <p className="text-xs text-destructive">{fieldErrors.execution_key}</p>}
      </div>

      <JSONEditor
        label="Input"
        value={inputJson}
        onChange={setInputJson}
        error={fieldErrors.input}
      />
      {inputValidationErrors.length > 0 && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-sm text-destructive font-medium mb-1">Input validation errors:</p>
          <ul className="text-sm text-destructive space-y-0.5">
            {inputValidationErrors.map(({ field, message }) => (
              <li key={field}><span className="font-mono">{field}</span>: {message}</li>
            ))}
          </ul>
        </div>
      )}

      {supportsFiles && (
        <div className="flex flex-col gap-1">
          <Label htmlFor="exec-files">Files (optional)</Label>
          <input
            id="exec-files"
            ref={fileInputRef}
            type="file"
            multiple
            accept=".txt,.pdf,.jpg,.jpeg,.png"
            onChange={e => setFiles(e.target.files ? Array.from(e.target.files) : [])}
            className="text-sm file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-sm file:bg-secondary file:text-secondary-foreground hover:file:bg-secondary/80 cursor-pointer"
          />
          {files.length > 0 && (
            <p className="text-xs text-muted-foreground">{files.length} file{files.length > 1 ? "s" : ""} selected</p>
          )}
          {fieldErrors.files && <p className="text-xs text-destructive">{fieldErrors.files}</p>}
        </div>
      )}
    </FormModal>
  );
}
