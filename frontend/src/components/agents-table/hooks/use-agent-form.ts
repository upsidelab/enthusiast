import { useState, useEffect } from "react";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { Agent } from "@/lib/types";
import {AgentChoice} from "@/lib/api/agents.ts";
import { ApiError } from "@/lib/api-error";

const apiClient = new ApiClient(authenticationProviderInstance);

export function useAgentForm(
  agent: Agent | null,
  agentTypes: AgentChoice[],
  dataSetId: number | null,
  onSuccess: () => void
) {
  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [config, setConfig] = useState<Record<string, string | number | boolean>>({});
  const [agentConfigSections, setAgentConfigSections] = useState<Record<string, Record<string, unknown> | Record<string, unknown>[]> >({});
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
          const flattenConfigForForm = (config: unknown): Record<string, string | number | boolean> => {
      const flattenedConfig: Record<string, string | number | boolean> = {};
      
      if (!config || typeof config !== 'object') {
        return flattenedConfig;
      }
      
      Object.entries(config as Record<string, unknown>).forEach(([section, sectionData]) => {
      if (Array.isArray(sectionData)) {
        sectionData.forEach(obj => {
          if (obj && typeof obj === 'object') {
            Object.entries(obj).forEach(([key, value]) => {
              if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
                flattenedConfig[`${section}_${key}`] = value;
              }
            });
          }
        });
      } else if (sectionData && typeof sectionData === 'object') {
        Object.entries(sectionData).forEach(([key, value]) => {
          if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
            flattenedConfig[`${section}_${key}`] = value;
          }
        });
      }
    });
    
    return flattenedConfig;
  };

    const loadAgentDetailsForEditing = async () => {
      if (!agent) return;
      
      try {
        const agentDetails = await apiClient.agents().getAgentById(agent.id);
        setName(agentDetails.name);
        setType(agentDetails.agent_type);
        
        const flattenedConfig = flattenConfigForForm(agentDetails.config);
        setConfig(flattenedConfig);
      } catch (error) {
        console.error('Failed to load agent details:', error);
      }
    };

    loadAgentDetailsForEditing();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agent?.id]);

  useEffect(() => {
    const resetFormForNewAgent = () => {
      if (!agent) {
        setName("");
        setType("");
        setConfig({});
        setAgentConfigSections({});
        setOpenSections({});
        setFieldErrors({});
        setGeneralError("");
      }
    };

    resetFormForNewAgent();
  }, [agent]);
  
  useEffect(() => {
    const clearFormWhenNoType = () => {
      if (!type) {
        setConfig({});
        setAgentConfigSections({});
        setOpenSections({});
        return true;
      }
      return false;
    };

    const extractConfigSectionsFromType = (selectedType: AgentChoice) => {
      const configSections: Record<string, Record<string, unknown> | Record<string, unknown>[]> = {};
      Object.entries(selectedType).forEach(([section, value]) => {
        if (section !== 'key' && section !== 'name' && value && typeof value === 'object') {
          configSections[section] = value;
        }
      });
      return configSections;
    };

    const initializeCollapsedSections = (configSections: Record<string, unknown>) => {
      const initialOpenSections: Record<string, boolean> = {};
      Object.keys(configSections).forEach(section => {
        initialOpenSections[section] = false;
      });
      return initialOpenSections;
    };

      const createDefaultConfigValues = (configSections: Record<string, unknown>) => {
    const defaults: Record<string, string | number | boolean> = {};
    Object.entries(configSections).forEach(([section, sectionData]) => {
      if (Array.isArray(sectionData)) {
        sectionData.forEach(obj => {
          if (obj && typeof obj === 'object') {
            Object.keys(obj).forEach(k => { defaults[`${section}_${k}`] = ""; });
          }
        });
      } else if (sectionData && typeof sectionData === 'object') {
        Object.keys(sectionData).forEach(k => { defaults[`${section}_${k}`] = ""; });
      }
    });
    return defaults;
  };

    const updateFormForSelectedType = () => {
      const wasCleared = clearFormWhenNoType();
      if (wasCleared) return;

      const selected = agentTypes.find((t) => t.key === type);
      if (!selected) return;

      const configSections = extractConfigSectionsFromType(selected);
      setAgentConfigSections(configSections);
      
      const initialOpenSections = initializeCollapsedSections(configSections);
      setOpenSections(initialOpenSections);
      
      if (!agent && Object.keys(config).length === 0) {
        const defaults = createDefaultConfigValues(configSections);
        setConfig(defaults);
      }
    };

    updateFormForSelectedType();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type, agentTypes, agent]);

  const handleConfigChange = (key: string, value: string) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const buildNestedConfigFromFlattened = () => {
    const configObj: Record<string, unknown> = {};
    Object.entries(agentConfigSections).forEach(([section, fields]) => {
      if (Array.isArray(fields)) {
        configObj[section] = buildToolsArrayConfig(section, fields);
      } else if (fields && typeof fields === 'object') {
        configObj[section] = buildRegularSectionConfig(section, fields);
      }
    });
    return configObj;
  };

  const buildToolsArrayConfig = (section: string, fields: Record<string, unknown>[]) => {
    return fields.map(obj => {
      const out: Record<string, string | number | boolean> = {};
      if (obj && typeof obj === 'object') {
        Object.keys(obj).forEach(k => {
          const v = config[`${section}_${k}`];
          if (v !== '' && v !== null && v !== undefined) out[k] = v;
        });
      }
      return out;
    });
  };

  const buildRegularSectionConfig = (section: string, fields: Record<string, unknown>) => {
    const out: Record<string, string | number | boolean> = {};
    Object.keys(fields).forEach(k => {
      const v = config[`${section}_${k}`];
      if (v !== '' && v !== null && v !== undefined) out[k] = v;
    });
    return out;
  };

  const saveAgentToApi = async (configObj: Record<string, unknown>) => {
    if (!dataSetId) return;
    
    const agentData = {
      name,
      agent_type: type,
      dataset: dataSetId,
      config: configObj
    };

    if (agent) {
      await apiClient.agents().updateAgent(agent.id, agentData);
    } else {
      await apiClient.agents().createAgent(agentData);
    }
  };

  const parseFieldErrors = (errorData: unknown) => {
    const newFieldErrors: Record<string, string> = {};
    
    parseBasicFieldErrors(errorData, newFieldErrors);
    parseConfigSectionErrors(errorData, newFieldErrors);
    
    return newFieldErrors;
  };

  const parseBasicFieldErrors = (errorData: unknown, newFieldErrors: Record<string, string>) => {
    if (typeof errorData === 'object' && errorData && 'name' in errorData) {
      const nameError = (errorData as { name: unknown }).name;
      if (Array.isArray(nameError)) {
        newFieldErrors.name = String(nameError[0]);
      } else if (typeof nameError === 'string') {
        newFieldErrors.name = nameError;
      }
    }
    if (typeof errorData === 'object' && errorData && 'agent_type' in errorData) {
      const typeError = (errorData as { agent_type: unknown }).agent_type;
      if (Array.isArray(typeError)) {
        newFieldErrors.type = String(typeError[0]);
      } else if (typeof typeError === 'string') {
        newFieldErrors.type = typeError;
      }
    }
  };

  const parseConfigSectionErrors = (errorData: unknown, newFieldErrors: Record<string, string>) => {
    if (typeof errorData !== 'object' || !errorData || !('config' in errorData)) return;
    
    const configErrors = (errorData as { config: unknown }).config;
    if (typeof configErrors !== 'object' || !configErrors) return;
    
    const sectionNames = ['agent_args', 'prompt_input', 'prompt_extension'];
    
    sectionNames.forEach(sectionName => {
      parseSingleConfigSection(sectionName, (configErrors as Record<string, unknown>)[sectionName], newFieldErrors);
    });
    
    parseToolsArrayErrors((configErrors as Record<string, unknown>).tools, newFieldErrors);
  };

  const parseSingleConfigSection = (sectionName: string, sectionErrors: unknown, newFieldErrors: Record<string, string>) => {
    if (sectionErrors && typeof sectionErrors === 'object') {
              Object.entries(sectionErrors as Record<string, unknown>).forEach(([field, error]) => {
        newFieldErrors[`${sectionName}_${field}`] = Array.isArray(error) ? String(error[0]) : String(error);
      });
    }
  };

  const parseToolsArrayErrors = (toolsErrors: unknown, newFieldErrors: Record<string, string>) => {
    if (toolsErrors && Array.isArray(toolsErrors)) {
              toolsErrors.forEach((toolErrors: unknown) => {
        if (toolErrors && typeof toolErrors === 'object') {
                      Object.entries(toolErrors as Record<string, unknown>).forEach(([field, error]) => {
                          newFieldErrors[`tools_${field}`] = Array.isArray(error) ? String(error[0]) : String(error);
          });
        }
      });
    }
  };

  const handleSubmit = async () => {
    if (!dataSetId) return;
    
    setSubmitting(true);
    setFieldErrors({});
    setGeneralError("");
    
    try {
      const configObj = buildNestedConfigFromFlattened();
      await saveAgentToApi(configObj);
      onSuccess();
    } catch (e) {
      if (e instanceof ApiError && e.response?.data) {
        const errorData = e.response.data;
        const newFieldErrors = parseFieldErrors(errorData);
        
        setFieldErrors(newFieldErrors);
        
        if (Object.keys(newFieldErrors).length === 0) {
          const errorDetail = typeof errorData === 'object' && errorData && 'detail' in errorData ? String(errorData.detail) : undefined;
          const errorMessage = typeof errorData === 'object' && errorData && 'message' in errorData ? String(errorData.message) : undefined;
          setGeneralError(errorDetail || errorMessage || 'Failed to save agent');
        }
      } else {
        setGeneralError(e instanceof Error ? e.message : 'Failed to save agent');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setName("");
    setType("");
    setConfig({});
    setAgentConfigSections({});
    setOpenSections({});
    setFieldErrors({});
    setGeneralError("");
  };

  return {
    name,
    setName,
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
    handleConfigChange,
    resetForm
  };
}
