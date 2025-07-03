import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog.tsx";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Textarea } from "@/components/ui/textarea.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { CatalogSource, SourcePlugin } from "@/lib/types.ts";

const api = new ApiClient(authenticationProviderInstance);

const formSchema = z.object({
  pluginName: z.string().min(1, "Plugin is required"),
  config: z.string().min(1, "Configuration is required"),
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
  const [isLoading, setIsLoading] = useState(false);
  const [configError, setConfigError] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      pluginName: source?.plugin_name || "",
      config: source ? JSON.stringify(source.config, null, 2) : "{}",
    },
  });

  const handleSubmit = async (data: FormData) => {
    setIsLoading(true);
    setConfigError(null);
    setApiError(null);
    
    try {
      let parsedConfig;
      try {
        parsedConfig = JSON.parse(data.config);
      } catch (jsonError) {
        console.error(jsonError);
        setConfigError("Invalid JSON format. Please check your configuration.");
        setIsLoading(false);
        return;
      }

      if (source) {
        const updatedSource: CatalogSource = {
          ...source,
          plugin_name: data.pluginName,
          config: data.config,
        };

        if (sourceType === 'product') {
          await api.dataSets().configureDataSetProductSource(updatedSource);
        } else {
          await api.dataSets().configureDataSetDocumentSource(updatedSource);
        }
      } else {
        if (sourceType === 'product') {
          await api.dataSets().addDataSetProductSource(dataSetId, data.pluginName, parsedConfig);
        } else {
          await api.dataSets().addDataSetDocumentSource(dataSetId, data.pluginName, parsedConfig);
        }
      }
      onSave();
    } catch (error) {
      console.error(error);
      setApiError("Failed to add source. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const isEditing = !!source;
  const title = isEditing ? `Edit ${sourceType} source` : `Add ${sourceType} source`;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="pluginName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Plugin</FormLabel>
                  <Select 
                    onValueChange={field.onChange} 
                    defaultValue={field.value}
                    disabled={isLoading || isEditing}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a plugin" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {availablePlugins.map((plugin) => (
                        <SelectItem key={plugin.plugin_name} value={plugin.plugin_name}>
                          {plugin.plugin_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Choose the plugin that will provide the data for this source.
                  </FormDescription>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="config"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Configuration</FormLabel>
                  {configError && (
                    <div className="text-red-500 text-sm mb-2">
                      {configError}
                    </div>
                  )}
                  <FormControl>
                    <Textarea 
                      placeholder="Enter configuration as JSON" 
                      className="min-h-[200px] font-mono text-sm"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormDescription>
                    Configuration parameters for the selected plugin. Please refer to the plugin documentation for required parameters.
                  </FormDescription>
                </FormItem>
              )}
            />

            {apiError && (
              <div className="text-red-500 text-sm mb-4">
                {apiError}
              </div>
            )}
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Saving..." : (isEditing ? "Update" : "Add")}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
} 
