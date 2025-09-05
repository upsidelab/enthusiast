import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { CatalogSource, SourcePlugin } from "@/lib/types.ts";
import { useSourceForm } from "./hooks/use-source-form.ts";
import { ConfigurationForm } from "@/components/ui/configuration-form.tsx";
import { FormModal } from "@/components/ui/form-modal";
import { useEffect } from "react";

const formSchema = z.object({
  pluginName: z.string().min(1, "Plugin is required"),
});

type FormData = z.infer<typeof formSchema>;

export interface AddEditSourceModalProps {
  dataSetId: number;
  sourceType: 'product' | 'document';
  source: CatalogSource | null;
  availablePlugins: SourcePlugin[];
  open: boolean;
  onClose: () => void;
  onSave: () => void;
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
    setConfig,
    fieldErrors,
    generalError,
    submitting,
    handleSubmit,
    getSelectedPlugin,
    resetForm
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
  const title = isEditing ? `Edit ${sourceType} source` : `Add ${sourceType} source`;

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
                <FormLabel>Plugin</FormLabel>
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
                  Choose the plugin that will provide the data for this source.
                </FormDescription>
                {fieldErrors.pluginName && (
                  <p className="text-xs text-destructive">{fieldErrors.pluginName}</p>
                )}
              </FormItem>
            )}
          />

          {selectedPlugin && (
            <ConfigurationForm
              configurationArgs={selectedPlugin.configuration_args}
              config={config}
              setConfig={setConfig}
              fieldErrors={fieldErrors}
            />
          )}
        </form>
      </Form>
    </FormModal>
  );
} 
