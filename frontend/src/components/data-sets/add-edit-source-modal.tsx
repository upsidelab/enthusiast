import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { CatalogSource, SourcePlugin } from "@/lib/types.ts";
import { useSourceForm } from "./hooks/use-source-form.ts";
import { FormModal } from "@/components/ui/form-modal";
import { useEffect } from "react";
import { RjsfForm } from "@/components/rjsf";

const SOURCE_SECTION_KEYS = ["configuration_args"] as const;
const SOURCE_SECTION_TITLES: Record<string, string> = { configuration_args: "Configuration" };

const formSchema = z.object({
  pluginName: z.string().min(1, "Plugin is required"),
});

type FormData = z.infer<typeof formSchema>;

export type IntegrationType = 'ecommerce' | 'product' | 'document';

export interface AddEditSourceModalProps {
  dataSetId: number;
  sourceType: IntegrationType;
  source: CatalogSource | null;
  availablePlugins: SourcePlugin[];
  open: boolean;
  onClose: () => void;
  onSave: () => void;
}

const titleByIntegrationType = {
  "ecommerce": "E-Commerce system",
  "product": "Product source",
  "document": "Document source",
}

export function AddEditSourceModal({
  dataSetId,
  sourceType,
  source,
  availablePlugins,
  onClose,
  onSave,
  open
}: AddEditSourceModalProps) {
  const {
    setPluginName,
    config,
    fieldErrors,
    generalError,
    submitting,
    handleSubmit,
    getSelectedPlugin,
    resetForm,
    openSections,
    setOpenSections,
    updateConfigSection,
  } = useSourceForm(source, availablePlugins, dataSetId, sourceType, onSave);

  // Reset form when modal closes
  useEffect(() => {
    if (!open) {
      resetForm();
    }
  }, [open, resetForm]);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      pluginName: source?.plugin_name || "",
    },
  });

  const selectedPlugin = getSelectedPlugin();

  const onSubmit = async () => {
    await handleSubmit();
  };

  const isEditing = !!source;
  const title = isEditing ? `Edit ${titleByIntegrationType[sourceType]} connection` : `Connect ${titleByIntegrationType[sourceType]}`;

  return (
    <FormModal
      open={open}
      onOpenChange={onClose}
      title={title}
      onSubmit={onSubmit}
      onCancel={onClose}
      submitLabel={isEditing ? "Update" : "Add"}
      submitting={submitting}
      disabled={!selectedPlugin}
      dependencies={[selectedPlugin, config, generalError, fieldErrors]}
    >
      {generalError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-sm text-destructive">{generalError}</p>
        </div>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="pluginName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Integration</FormLabel>
                <Select 
                  onValueChange={(value) => {
                    field.onChange(value);
                    setPluginName(value);
                  }}
                  defaultValue={field.value}
                  disabled={submitting || isEditing}
                >
                  <FormControl>
                    <SelectTrigger className={fieldErrors.pluginName ? "border-destructive" : ""}>
                      <SelectValue placeholder="Select a plugin" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {availablePlugins.map((plugin) => (
                      <SelectItem key={plugin.name} value={plugin.name}>
                        {plugin.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormDescription>
                  The connector to use.
                </FormDescription>
                {fieldErrors.pluginName && (
                  <p className="text-xs text-destructive">{fieldErrors.pluginName}</p>
                )}
              </FormItem>
            )}
          />

          {selectedPlugin && (
            <RjsfForm
              choice={selectedPlugin}
              config={config}
              sectionKeys={SOURCE_SECTION_KEYS}
              sectionTitles={SOURCE_SECTION_TITLES}
              onConfigChange={updateConfigSection}
              fieldErrors={fieldErrors}
              openSections={openSections}
              onOpenSectionsChange={setOpenSections}
              showToolsSection={false}
              header={
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-foreground">Configuration</h4>
                  <p className="text-xs text-muted-foreground">Configure connection parameters</p>
                </div>
              }
              emptyMessage={
                <>
                  <p className="text-sm text-muted-foreground mb-2">No configuration required</p>
                  <p className="text-xs text-muted-foreground">
                    This connector doesn't require any additional configuration.
                  </p>
                </>
              }
            />
          )}
        </form>
      </Form>
    </FormModal>
  );
} 
