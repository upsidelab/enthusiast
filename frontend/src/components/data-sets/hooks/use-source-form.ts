import { useState, useEffect } from "react";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { CatalogSource, SourcePlugin } from "@/lib/types";
import { ApiError } from "@/lib/api-error";
import { flattenConfigForForm, buildConfigFromFlattened, parseFieldErrors as parseFieldErrorsBase } from "@/lib/form-utils";

const apiClient = new ApiClient(authenticationProviderInstance);

export function useSourceForm(
  source: CatalogSource | null,
  availablePlugins: SourcePlugin[],
  dataSetId: number | null,
  sourceType: 'product' | 'document',
  onSuccess: () => void
) {
  const [pluginName, setPluginName] = useState("");
  const [config, setConfig] = useState<Record<string, string | number | boolean>>({});
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const loadSourceDetailsForEditing = async () => {
      if (!source) return;
      
      try {
        setPluginName(source.plugin_name);
        const currentPlugin = availablePlugins.find(p => p.name === source.plugin_name);
        if (currentPlugin && Object.keys(currentPlugin.configuration_args).length > 0) {
          const flattenedConfig = flattenConfigForForm(source.config, {
            'configuration_args': 'configuration'
          });
          setConfig(flattenedConfig);
        } else {
          setConfig({});
        }
      } catch {
        setGeneralError('Failed to load source details');
      }
    };

    loadSourceDetailsForEditing();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source?.id, availablePlugins]);

  useEffect(() => {
    const resetFormForNewSource = () => {
      if (!source) {
        setPluginName("");
        setConfig({});
        setOpenSections({});
        setFieldErrors({});
        setGeneralError("");
      }
    };

    resetFormForNewSource();
  }, [source]);

  useEffect(() => {
    const clearFormWhenNoPlugin = () => {
      if (!pluginName) {
        if (source?.id) {
          return false;
        }
        setConfig({});
        setOpenSections({});
        return true;
      }
      return false;
    };

    const getSelectedPlugin = () => {
      return availablePlugins.find((p) => p.name === pluginName);
    };

    const initializeCollapsedSections = () => {
      const selectedPlugin = getSelectedPlugin();
      if (!selectedPlugin) return {};

      const initialOpenSections: Record<string, boolean> = {};
      if (Object.keys(selectedPlugin.configuration_args).length > 0) {
        initialOpenSections['configuration'] = true;
      }
      return initialOpenSections;
    };

    const createDefaultConfigValues = () => {
      const selectedPlugin = getSelectedPlugin();
      if (!selectedPlugin) return {};

      const defaults: Record<string, string | number | boolean> = {};
      Object.entries(selectedPlugin.configuration_args).forEach(([key, schema]) => {
        const configKey = `configuration_${key}`;
        if (schema.type.inner_type === 'Json') {
          defaults[configKey] = '{}';
        } else {
          defaults[configKey] = '';
        }
      });
      return defaults;
    };

    const updateFormForSelectedPlugin = () => {
      const wasCleared = clearFormWhenNoPlugin();
      if (wasCleared) {
        return;
      }

      const selectedPlugin = getSelectedPlugin();
      if (!selectedPlugin) {
        return;
      }

      const initialOpenSections = initializeCollapsedSections();
      setOpenSections(initialOpenSections);
      
      if (!source?.id && Object.keys(config).length === 0) {
        const defaults = createDefaultConfigValues();
        setConfig(defaults);
      }
    };

    updateFormForSelectedPlugin();
  }, [pluginName, availablePlugins, source, config, setConfig, setOpenSections]);

  const saveSourceToApi = async (configObj: Record<string, unknown>) => {
    if (source) {
      const updatedSource: CatalogSource = {
        ...source,
        plugin_name: pluginName,
        config: JSON.stringify(configObj),
      };
      
      if (sourceType === 'product') {
        await apiClient.dataSets().configureDataSetProductSource(updatedSource);
      } else {
        await apiClient.dataSets().configureDataSetDocumentSource(updatedSource);
      }
    } else {
      if (sourceType === 'product') {
        await apiClient.dataSets().addDataSetProductSource(dataSetId!, pluginName, configObj);
      } else {
        await apiClient.dataSets().addDataSetDocumentSource(dataSetId!, pluginName, configObj);
      }
    }
    onSuccess();
  };

  const parseFieldErrors = (errorData: unknown) => {
    const newFieldErrors = parseFieldErrorsBase(errorData);
    
    // Handle plugin name errors specifically for sources
    if (typeof errorData === 'object' && errorData && 'plugin_name' in errorData) {
      const pluginNameError = (errorData as Record<string, unknown>).plugin_name;
      if (Array.isArray(pluginNameError)) {
        newFieldErrors['pluginName'] = String(pluginNameError[0]);
      }
    }

    return newFieldErrors;
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setFieldErrors({});
    setGeneralError("");

    try {
      const configObj = buildConfigFromFlattened(config, {
        'configuration': 'configuration_args'
      });
      await saveSourceToApi(configObj);
    } catch (error) {
      if (error instanceof ApiError) {
        const fieldErrors = parseFieldErrors(error.response.data);
        setFieldErrors(fieldErrors);
        
        if (Object.keys(fieldErrors).length === 0) {
          setGeneralError(error.message || "Failed to save source");
        }
      } else {
        setGeneralError("Failed to save source");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const getSelectedPlugin = () => {
    return availablePlugins.find((p) => p.name === pluginName);
  };

  const resetForm = () => {
    setPluginName("");
    setConfig({});
    setOpenSections({});
    setFieldErrors({});
    setGeneralError("");
  };

  return {
    pluginName,
    setPluginName,
    config,
    setConfig,
    openSections,
    setOpenSections,
    fieldErrors,
    generalError,
    submitting,
    handleSubmit,
    getSelectedPlugin,
    resetForm,
  };
}
