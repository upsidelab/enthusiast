import { useState, useEffect, useCallback, useRef } from "react";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { CatalogSource, SourcePlugin } from "@/lib/types";
import { ApiError } from "@/lib/api-error";
import { parseFieldErrors as parseFieldErrorsBase } from "@/lib/form-utils";
import { getDefaultFormData } from "@/components/rjsf";

const apiClient = new ApiClient(authenticationProviderInstance);

const SOURCE_SECTION_KEYS = ["configuration_args"] as const;

export function useSourceForm(
  source: CatalogSource | null,
  availablePlugins: SourcePlugin[],
  dataSetId: number | null,
  sourceType: "ecommerce" | "product" | "document",
  onSuccess: () => void
) {
  const [pluginName, setPluginName] = useState("");
  const [config, setConfig] = useState<Record<string, unknown>>({});
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const prevPluginRef = useRef<string>("");

  const getSelectedPlugin = useCallback(
    () => availablePlugins.find((p) => p.name === pluginName) ?? null,
    [availablePlugins, pluginName]
  );

  useEffect(() => {
    const loadSourceDetailsForEditing = async () => {
      if (!source) return;
      try {
        setPluginName(source.plugin_name);
        const currentPlugin = availablePlugins.find((p) => p.name === source.plugin_name);
        if (currentPlugin) {
          let parsed: Record<string, unknown> = {};
          try {
            parsed = typeof source.config === "string" ? JSON.parse(source.config) : (source.config as Record<string, unknown>);
          } catch {
            parsed = {};
          }
          const normalized =
            parsed && typeof parsed === "object" && "configuration_args" in parsed
              ? (parsed as Record<string, unknown>)
              : { configuration_args: parsed };
          setConfig(normalized);
        } else {
          setConfig({});
        }
      } catch {
        setGeneralError("Failed to load source details");
      }
    };
    loadSourceDetailsForEditing();
  }, [source, availablePlugins]);

  useEffect(() => {
    if (!source) {
      setPluginName("");
      setConfig({});
      setOpenSections({});
      setFieldErrors({});
      setGeneralError("");
    }
  }, [source]);

  useEffect(() => {
    if (!pluginName) {
      setConfig({});
      setOpenSections({});
      prevPluginRef.current = "";
      return;
    }
    const plugin = getSelectedPlugin();
    if (!plugin) return;
    const configArgs = plugin.configuration_args;
    if (configArgs && typeof configArgs === "object" && !Array.isArray(configArgs) && Object.keys(configArgs).length > 0) {
      setOpenSections((prev) => ({ ...prev, configuration_args: false }));
    }
    if (!source && prevPluginRef.current !== pluginName) {
      setConfig(getDefaultFormData(plugin, SOURCE_SECTION_KEYS));
      prevPluginRef.current = pluginName;
    }
  }, [pluginName, getSelectedPlugin, source]);

  const updateConfigSection = useCallback((key: string, value: unknown) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  }, []);

  const saveSourceToApi = useCallback(
    async (configObj: Record<string, unknown>) => {
      if (source) {
        const updatedSource: CatalogSource = {
          ...source,
          plugin_name: pluginName,
          config: JSON.stringify(configObj),
        };
        if (sourceType === "product") {
          await apiClient.dataSets().configureDataSetProductSource(updatedSource);
        } else if (sourceType === "document") {
          await apiClient.dataSets().configureDataSetDocumentSource(updatedSource);
        } else if (sourceType === "ecommerce") {
          await apiClient.dataSets().configureDataSetECommerceIntegration(updatedSource);
        }
      } else {
        if (sourceType === "product") {
          await apiClient.dataSets().addDataSetProductSource(dataSetId!, pluginName, configObj);
        } else if (sourceType === "document") {
          await apiClient.dataSets().addDataSetDocumentSource(dataSetId!, pluginName, configObj);
        } else if (sourceType === "ecommerce") {
          await apiClient.dataSets().addDataSetECommerceIntegration(dataSetId!, pluginName, configObj);
        }
      }
      onSuccess();
    },
    [dataSetId, pluginName, source, sourceType, onSuccess]
  );

  const parseFieldErrors = useCallback((errorData: unknown): Record<string, string> => {
    const newFieldErrors = parseFieldErrorsBase(errorData);
    if (typeof errorData === "object" && errorData && "plugin_name" in errorData) {
      const pluginNameError = (errorData as Record<string, unknown>).plugin_name;
      if (Array.isArray(pluginNameError) && pluginNameError.length > 0) {
        newFieldErrors.pluginName = String(pluginNameError[0]);
      } else if (typeof pluginNameError === "string") {
        newFieldErrors.pluginName = pluginNameError;
      }
    }
    if (typeof errorData === "object" && errorData && "config" in errorData) {
      const configErrors = (errorData as { config: unknown }).config;
      if (typeof configErrors === "object" && configErrors) {
        const cfg = configErrors as Record<string, unknown>;
        const section = cfg.configuration_args;
        if (section && typeof section === "object") {
          Object.entries(section as Record<string, unknown>).forEach(([field, error]) => {
            newFieldErrors[`configuration_args.${field}`] = Array.isArray(error) ? String(error[0]) : String(error);
          });
        }
      }
    }
    return newFieldErrors;
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!dataSetId && !source) return;
    setSubmitting(true);
    setFieldErrors({});
    setGeneralError("");
    try {
      await saveSourceToApi(config);
      onSuccess();
    } catch (e) {
      if (e instanceof ApiError && e.response?.data) {
        const newFieldErrors = parseFieldErrors(e.response.data);
        setFieldErrors(newFieldErrors);
        if (Object.keys(newFieldErrors).length === 0) {
          const detail =
            typeof e.response.data === "object" && e.response.data && "detail" in e.response.data
              ? String((e.response.data as { detail: unknown }).detail)
              : undefined;
          const message =
            typeof e.response.data === "object" && e.response.data && "message" in e.response.data
              ? String((e.response.data as { message: unknown }).message)
              : undefined;
          setGeneralError(detail ?? message ?? "Failed to save source");
        }
      } else {
        setGeneralError(e instanceof Error ? e.message : "Failed to save source");
      }
    } finally {
      setSubmitting(false);
    }
  }, [dataSetId, source, config, saveSourceToApi, parseFieldErrors, onSuccess]);

  const resetForm = useCallback(() => {
    setPluginName("");
    setConfig({});
    setOpenSections({});
    setFieldErrors({});
    setGeneralError("");
  }, []);

  return {
    pluginName,
    setPluginName,
    config,
    setConfig,
    openSections,
    setOpenSections,
    updateConfigSection,
    fieldErrors,
    generalError,
    submitting,
    handleSubmit,
    getSelectedPlugin,
    resetForm,
  };
}
