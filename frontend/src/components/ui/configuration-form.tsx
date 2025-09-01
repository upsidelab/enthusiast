import { DynamicConfigInput } from "@/components/agents-table/dynamic-config-input";
import { ExtraArgDetail } from "@/lib/types";

interface ConfigurationFormProps {
  configurationArgs: Record<string, ExtraArgDetail>;
  config: Record<string, string | number | boolean>;
  setConfig: (config: Record<string, string | number | boolean>) => void;
  fieldErrors: Record<string, string>;
  prefix?: string;
}

export function ConfigurationForm({
  configurationArgs,
  config,
  setConfig,
  fieldErrors,
  prefix = "configuration"
}: ConfigurationFormProps) {
  if (!configurationArgs || Object.keys(configurationArgs).length === 0) {
    return null;
  }

  const handleFieldChange = (key: string, value: string | number | boolean) => {
    const newConfig = { ...config, [`${prefix}_${key}`]: value };
    setConfig(newConfig);
  };

  return (
    <div className="space-y-4">
      {Object.entries(configurationArgs).map(([key, schema]) => {
        const configKey = `${prefix}_${key}`;
        const currentValue = config[configKey] || '';
        const error = fieldErrors[configKey];

        return (
          <div key={key} className="space-y-2">
            <DynamicConfigInput
              id={`config-${configKey}`}
              label={schema.title || key}
              description={schema.description || undefined}
              typeInfo={schema.type}
              value={currentValue}
              onChange={(value) => handleFieldChange(key, value)}
              error={error}
            />
          </div>
        );
      })}
    </div>
  );
}
