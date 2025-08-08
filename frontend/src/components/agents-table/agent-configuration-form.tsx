import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDownIcon, ChevronRightIcon } from "lucide-react";
import { useEffect } from "react";
import { DynamicConfigInput } from "./dynamic-config-input";
import { TypeInfo } from "@/lib/types";

interface AgentConfigurationFormProps {
  agentConfigSections: Record<string, Record<string, unknown> | Record<string, unknown>[]>;
  openSections: Record<string, boolean>;
  setOpenSections: (sections: Record<string, boolean>) => void;
  config: Record<string, string | number | boolean>;
  setConfig: (config: Record<string, string | number | boolean>) => void;
  fieldErrors: Record<string, string>;
}

export function AgentConfigurationForm({
  agentConfigSections,
  openSections,
  setOpenSections,
  config,
  setConfig,
  fieldErrors
}: AgentConfigurationFormProps) {
  const handleConfigChange = (key: string, value: string | number | boolean) => {
    setConfig({ ...config, [key]: value });
  };

  useEffect(() => {
    const checkForSectionErrors = (section: string, fields: Record<string, unknown> | Record<string, unknown>[]) => {
      if (Array.isArray(fields)) {
        return fields.some(obj => {
          if (obj && typeof obj === 'object') {
            return Object.keys(obj).some(key => fieldErrors[`${section}_${key}`]);
          }
          return false;
        });
      } else if (fields && typeof fields === 'object') {
        return Object.keys(fields).some(key => fieldErrors[`${section}_${key}`]);
      }
      return false;
    };

    const expandSectionsWithErrors = () => {
      if (Object.keys(fieldErrors).length === 0) return;

      const sectionsToExpand: Record<string, boolean> = { ...openSections };
      let hasChanges = false;

      Object.entries(agentConfigSections).forEach(([section, fields]) => {
        const sectionHasErrors = checkForSectionErrors(section, fields);
        
        if (sectionHasErrors && !openSections[section]) {
          sectionsToExpand[section] = true;
          hasChanges = true;
        }
      });

      if (hasChanges) {
        setOpenSections(sectionsToExpand);
      }
    };

    expandSectionsWithErrors();
  }, [fieldErrors, agentConfigSections, openSections, setOpenSections]);

  const hasConfigFields = Object.values(agentConfigSections).some(section => {
    if (Array.isArray(section)) {
      return section.some(obj => obj && typeof obj === 'object' && Object.keys(obj).length > 0);
    } else if (section && typeof section === 'object') {
      return Object.keys(section).length > 0;
    }
    return false;
  });

  const renderConfigField = (key: string, schema: unknown, configKey: string) => {
    const s = schema as Record<string, unknown>;
    const fieldTitle = (s && typeof s.title === 'string') ? s.title || key : String(key);
    const typeInfo = s?.type as TypeInfo | undefined;
    const description = typeof s?.description === 'string' ? s.description : undefined;
    const currentValue = config[configKey] ?? '';
    
    return (
      <DynamicConfigInput
        key={key}
        id={`agent-arg-${configKey}`}
        label={fieldTitle}
        placeholder={fieldTitle}
        value={currentValue}
        onChange={(value) => handleConfigChange(configKey, value)}
        typeInfo={typeInfo}
        description={description}
        error={fieldErrors[configKey]}
      />
    );
  };

  const renderToolsArrayFields = (section: string, fields: Record<string, unknown>[]) => {
    return fields.map((obj, idx) => {
      const sObj = obj && typeof obj === 'object' ? obj : {};
      if (Object.keys(sObj).length === 0) return null;
      
      return (
        <div key={idx} className="pl-4 border-l-2 border-muted bg-muted/20 rounded-r-md p-3">
          <div className="space-y-3">
            {Object.entries(sObj).map(([key, schema]) => {
              const configKey = `${section}_${key}`;
              return typeof key === 'string' ? renderConfigField(key, schema, configKey) : null;
            })}
          </div>
        </div>
      );
    });
  };

  const renderRegularFields = (section: string, fields: Record<string, unknown>) => {
    return Object.entries(fields).map(([key, schema]) => {
      const configKey = `${section}_${key}`;
      return typeof key === 'string' ? renderConfigField(key, schema, configKey) : null;
    });
  };

  const renderConfigSection = (section: string, fields: Record<string, unknown> | Record<string, unknown>[]) => {
    let hasFields = false;
    if (Array.isArray(fields)) {
      hasFields = fields.some(obj => obj && typeof obj === 'object' && Object.keys(obj).length > 0);
    } else if (fields && typeof fields === 'object') {
      hasFields = Object.keys(fields).length > 0;
    }
    if (!hasFields) return null;

    const sectionTitle = String(section).replace(/_/g, ' ');

    return (
      <Collapsible 
        key={section} 
        open={openSections[section]} 
        onOpenChange={(open) => setOpenSections({ ...openSections, [section]: open })}
      >
        <CollapsibleTrigger asChild>
          <Button variant="ghost" className="w-full justify-between p-0 h-auto">
            <div className="flex items-center gap-2">
              {openSections[section] ? <ChevronDownIcon className="h-4 w-4" /> : <ChevronRightIcon className="h-4 w-4" />}
              <span className="text-sm font-medium text-foreground capitalize">
                {sectionTitle}
              </span>
            </div>
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="space-y-4 mt-2">
          <div className="pl-4 space-y-4">
            {Array.isArray(fields)
              ? renderToolsArrayFields(section, fields)
              : renderRegularFields(section, fields as Record<string, unknown>)}
          </div>
        </CollapsibleContent>
      </Collapsible>
    );
  };

  if (!hasConfigFields) {
    return (
      <div className="p-4 bg-muted/20 rounded-md border border-dashed border-muted-foreground/20">
        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-2">No configuration required</p>
          <p className="text-xs text-muted-foreground">This agent type doesn't require any additional configuration parameters.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-foreground">Configuration</h4>
        <p className="text-xs text-muted-foreground">Configure agent parameters</p>
      </div>
      
      {Object.entries(agentConfigSections).map(([section, fields]) => 
        renderConfigSection(section, fields)
      )}
    </div>
  );
}
