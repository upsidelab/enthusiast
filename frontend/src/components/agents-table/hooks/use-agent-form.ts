import { useState, useEffect, useCallback, useRef } from "react";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { Agent } from "@/lib/types";
import type { AgentChoice } from "@/lib/api/agents";
import { ApiError } from "@/lib/api-error";
import type { AgentConfig } from "@/lib/types";
import { AGENT_CONFIG_SECTION_KEYS } from "@/lib/types";
import { parseFieldErrors as parseFieldErrorsBase } from "@/lib/form-utils";
import { getDefaultFormData } from "@/components/rjsf";

const apiClient = new ApiClient(authenticationProviderInstance);

export function useAgentForm(
  agent: Agent | null,
  agentTypes: AgentChoice[],
  dataSetId: number | null,
  onSuccess: () => void
) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [type, setType] = useState("");
  const [config, setConfig] = useState<AgentConfig>({});
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);

  const selectedType = type ? agentTypes.find((t) => t.key === type) ?? null : null;
  const prevTypeRef = useRef<string>("");

  useEffect(() => {
    const loadAgentDetailsForEditing = async () => {
      if (!agent) return;
      try {
        const agentDetails = await apiClient.agents().getAgentById(agent.id);
        setName(agentDetails.name);
        setDescription(agentDetails.description || "");
        setType(agentDetails.agent_type);
        setConfig(agentDetails.config ?? {});
      } catch (error) {
        console.error("Failed to load agent details:", error);
      }
    };
    loadAgentDetailsForEditing();
  }, [agent]);

  useEffect(() => {
    if (!agent) {
      setName("");
      setDescription("");
      setType("");
      setConfig({});
      setOpenSections({});
      setFieldErrors({});
      setGeneralError("");
    }
  }, [agent]);

  useEffect(() => {
    if (!type) {
      setConfig({});
      setOpenSections({});
      prevTypeRef.current = "";
      return;
    }
    const choice = agentTypes.find((t) => t.key === type);
    if (!choice) return;
    const sections: Record<string, boolean> = {};
    AGENT_CONFIG_SECTION_KEYS.forEach((key) => {
      const section = choice[key];
      if (section && typeof section === "object" && !Array.isArray(section) && Object.keys(section).length > 0) sections[key] = false;
    });
    if (Array.isArray(choice.tools) && choice.tools.length > 0) sections.tools = false;
    setOpenSections((prev) => ({ ...sections, ...prev }));
    if (!agent) {
      setName(choice.name);
      if (prevTypeRef.current !== type) {
        setConfig(getDefaultFormData(choice, AGENT_CONFIG_SECTION_KEYS) as AgentConfig);
        prevTypeRef.current = type;
      }
    }
  }, [type, agentTypes, agent]);

  const updateConfigSection = useCallback((section: keyof AgentConfig, value: unknown) => {
    setConfig((prev) => ({ ...prev, [section]: value }));
  }, []);

  const saveAgentToApi = useCallback(
    async (configObj: AgentConfig) => {
      if (!dataSetId) return;
      const agentData = {
        name,
        description,
        agent_type: type,
        dataset: dataSetId,
        config: configObj,
      };
      if (agent) {
        await apiClient.agents().updateAgent(agent.id, agentData);
      } else {
        await apiClient.agents().createAgent(agentData);
      }
    },
    [dataSetId, name, description, type, agent]
  );

  const parseFieldErrors = useCallback((errorData: unknown): Record<string, string> => {
    const newFieldErrors = parseFieldErrorsBase(errorData);
    if (typeof errorData === "object" && errorData && "config" in errorData) {
      const configErrors = (errorData as { config: unknown }).config;
      if (typeof configErrors === "object" && configErrors) {
        const cfg = configErrors as Record<string, unknown>;
        AGENT_CONFIG_SECTION_KEYS.forEach((sectionName) => {
          const section = cfg[sectionName];
          if (section && typeof section === "object") {
            Object.entries(section as Record<string, unknown>).forEach(([field, error]) => {
              newFieldErrors[`${sectionName}.${field}`] = Array.isArray(error) ? String(error[0]) : String(error);
            });
          }
        });
        const toolsErrors = cfg.tools;
        if (Array.isArray(toolsErrors)) {
          toolsErrors.forEach((toolErrors: unknown, idx: number) => {
            if (toolErrors && typeof toolErrors === "object") {
              Object.entries(toolErrors as Record<string, unknown>).forEach(([field, error]) => {
                newFieldErrors[`tools.${idx}.${field}`] = Array.isArray(error) ? String(error[0]) : String(error);
              });
            }
          });
        }
      }
    }
    return newFieldErrors;
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!dataSetId) return;
    setSubmitting(true);
    setFieldErrors({});
    setGeneralError("");
    try {
      await saveAgentToApi(config);
      onSuccess();
    } catch (e) {
      if (e instanceof ApiError && e.response?.data) {
        const errorData = e.response.data;
        const newFieldErrors = parseFieldErrors(errorData);
        setFieldErrors(newFieldErrors);
        if (Object.keys(newFieldErrors).length === 0) {
          const detail = typeof errorData === "object" && errorData && "detail" in errorData ? String((errorData as { detail: unknown }).detail) : undefined;
          const message = typeof errorData === "object" && errorData && "message" in errorData ? String((errorData as { message: unknown }).message) : undefined;
          setGeneralError(detail || message || "Failed to save agent");
        }
      } else {
        setGeneralError(e instanceof Error ? e.message : "Failed to save agent");
      }
    } finally {
      setSubmitting(false);
    }
  }, [dataSetId, config, saveAgentToApi, parseFieldErrors, onSuccess]);

  const resetForm = useCallback(() => {
    setName("");
    setDescription("");
    setType("");
    setConfig({});
    setOpenSections({});
    setFieldErrors({});
    setGeneralError("");
  }, []);

  return {
    name,
    setName,
    description,
    setDescription,
    type,
    setType,
    config,
    updateConfigSection,
    selectedType,
    openSections,
    setOpenSections,
    fieldErrors,
    generalError,
    submitting,
    handleSubmit,
    resetForm,
  };
}
