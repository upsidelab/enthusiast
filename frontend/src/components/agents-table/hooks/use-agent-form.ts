import { useState, useEffect } from "react";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { Agent } from "@/lib/types";

const apiClient = new ApiClient(authenticationProviderInstance);

export function useAgentForm(
  agent: Agent | null,
  agentTypes: any[],
  dataSetId: number | null,
  onSuccess: () => void
) {
  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [config, setConfig] = useState<Record<string, string | number | boolean>>({});
  const [agentConfigSections, setAgentConfigSections] = useState<Record<string, Record<string, any> | Record<string, any>[]> >({});
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
      const flattenConfigForForm = (config: any): Record<string, string | number | boolean> => {
    const flattenedConfig: Record<string, string | number | boolean> = {};
    
    Object.entries(config).forEach(([section, sectionData]) => {
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

    const extractConfigSectionsFromType = (selectedType: any) => {
      const configSections: Record<string, Record<string, any> | Record<string, any>[]> = {};
      Object.entries(selectedType).forEach(([section, value]) => {
        if (section !== 'key' && section !== 'name' && value && typeof value === 'object') {
          configSections[section] = value;
        }
      });
      return configSections;
    };

    const initializeCollapsedSections = (configSections: Record<string, any>) => {
      const initialOpenSections: Record<string, boolean> = {};
      Object.keys(configSections).forEach(section => {
        initialOpenSections[section] = false;
      });
      return initialOpenSections;
    };

      const createDefaultConfigValues = (configSections: Record<string, any>) => {
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

      const selected = agentTypes.find((t: any) => t.key === type);
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
  }, [type, agentTypes, agent]);

  const handleConfigChange = (key: string, value: string) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const buildNestedConfigFromFlattened = () => {
    const configObj: any = {};
    Object.entries(agentConfigSections).forEach(([section, fields]) => {
      if (Array.isArray(fields)) {
        configObj[section] = buildToolsArrayConfig(section, fields);
      } else if (fields && typeof fields === 'object') {
        configObj[section] = buildRegularSectionConfig(section, fields);
      }
    });
    return configObj;
  };

  const buildToolsArrayConfig = (section: string, fields: Record<string, any>[]) => {
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

  const buildRegularSectionConfig = (section: string, fields: Record<string, any>) => {
    const out: Record<string, string | number | boolean> = {};
    Object.keys(fields).forEach(k => {
      const v = config[`${section}_${k}`];
      if (v !== '' && v !== null && v !== undefined) out[k] = v;
    });
    return out;
  };

  const saveAgentToApi = async (configObj: any) => {
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

  const parseFieldErrors = (errorData: any) => {
    const newFieldErrors: Record<string, string> = {};
    
    parseBasicFieldErrors(errorData, newFieldErrors);
    parseConfigSectionErrors(errorData, newFieldErrors);
    
    return newFieldErrors;
  };

  const parseBasicFieldErrors = (errorData: any, newFieldErrors: Record<string, string>) => {
    if (errorData.name) {
      newFieldErrors.name = Array.isArray(errorData.name) ? errorData.name[0] : errorData.name;
    }
    if (errorData.agent_type) {
      newFieldErrors.type = Array.isArray(errorData.agent_type) ? errorData.agent_type[0] : errorData.agent_type;
    }
  };

  const parseConfigSectionErrors = (errorData: any, newFieldErrors: Record<string, string>) => {
    if (!errorData.config) return;
    
    const configErrors = errorData.config;
    const sectionNames = ['agent_args', 'prompt_input', 'prompt_extension'];
    
    sectionNames.forEach(sectionName => {
      parseSingleConfigSection(sectionName, configErrors[sectionName], newFieldErrors);
    });
    
    parseToolsArrayErrors(configErrors.tools, newFieldErrors);
  };

  const parseSingleConfigSection = (sectionName: string, sectionErrors: any, newFieldErrors: Record<string, string>) => {
    if (sectionErrors && typeof sectionErrors === 'object') {
      Object.entries(sectionErrors).forEach(([field, error]: [string, any]) => {
        newFieldErrors[`${sectionName}_${field}`] = Array.isArray(error) ? error[0] : error;
      });
    }
  };

  const parseToolsArrayErrors = (toolsErrors: any, newFieldErrors: Record<string, string>) => {
    if (toolsErrors && Array.isArray(toolsErrors)) {
      toolsErrors.forEach((toolErrors: any) => {
        if (toolErrors && typeof toolErrors === 'object') {
          Object.entries(toolErrors).forEach(([field, error]: [string, any]) => {
            newFieldErrors[`tools_${field}`] = Array.isArray(error) ? error[0] : error;
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
    } catch (e: any) {
      if (e.response?.data) {
        const errorData = e.response.data;
        const newFieldErrors = parseFieldErrors(errorData);
        
        setFieldErrors(newFieldErrors);
        
        if (Object.keys(newFieldErrors).length === 0) {
          setGeneralError(errorData.detail || errorData.message || 'Failed to save agent');
        }
      } else {
        setGeneralError(e.message || 'Failed to save agent');
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
