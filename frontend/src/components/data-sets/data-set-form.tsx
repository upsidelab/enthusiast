import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible.tsx";
import { useEffect, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { DataSet, ProvidersConfig } from "@/lib/types.ts";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";
import { InfoIcon } from "lucide-react";
import { formSchema, DataSetFormSchema } from "./data-set-form-schema.ts";
import { Label } from "@/components/ui/label.tsx";

const api = new ApiClient(authenticationProviderInstance);

interface DataSetFormProps {
  initialData?: DataSet;
  onSubmit: (values: DataSetFormSchema) => Promise<void>;
  submitButtonText: string;
  isOnboarding?: boolean;
  disabledFields?: string[];
}

// Helper component to show disabled field message
function DisabledFieldMessage() {
  return (
    <Alert className="mb-4">
      <div className="flex items-start gap-2">
        <InfoIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
        <AlertDescription>
          Some fields cannot be edited on existing data sets as they affect the underlying data structure.
        </AlertDescription>
      </div>
    </Alert>
  );
}

export function DataSetForm({ initialData, onSubmit, submitButtonText, isOnboarding = false, disabledFields = [] }: DataSetFormProps) {
  const [providersConfig, setProvidersConfig] = useState<ProvidersConfig | undefined>(undefined);
  const [languageModelNames, setLanguageModelNames] = useState<string[] | undefined>(undefined);
  const [embeddingModels, setEmbeddingModels] = useState<string[] | undefined>(undefined);

  const form = useForm<DataSetFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: initialData?.name || (isOnboarding ? "Default" : ""),
      languageModelProvider: initialData?.languageModelProvider || undefined,
      languageModel: initialData?.languageModel || undefined,
      embeddingProvider: initialData?.embeddingProvider || undefined,
      embeddingModel: initialData?.embeddingModel || undefined,
      embeddingVectorSize: initialData?.embeddingVectorSize || 512,
    }
  });

  useEffect(() => {
    const loadProvidersConfig = async () => {
      const result = await api.config().getAvailableProviders();
      setProvidersConfig(result);
      
      // Set default values if not already set
      if (!form.getValues('languageModelProvider') && result.languageModelProviders.length > 0) {
        form.setValue("languageModelProvider", result.languageModelProviders[0]);
      }
      if (!form.getValues('embeddingProvider') && result.embeddingProviders.length > 0) {
        form.setValue("embeddingProvider", result.embeddingProviders[0]);
      }
    }

    loadProvidersConfig();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const languageModelProvider = form.watch('languageModelProvider');

  useEffect(() => {
    const loadLanguageModels = async () => {
      if (languageModelProvider) {
        setLanguageModelNames(undefined);
        const result = await api.config().getLanguageModelsForProvider(languageModelProvider);
        setLanguageModelNames(result);
        
        // Set default value if not already set
        if (!form.getValues('languageModel') && result.length > 0) {
          form.setValue("languageModel", result[0]);
        }
      }
    }
    loadLanguageModels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [languageModelProvider]);

  const embeddingProvider = form.watch('embeddingProvider');

  useEffect(() => {
    const loadEmbeddingModels = async () => {
      if (embeddingProvider) {
        setEmbeddingModels(undefined);
        const result = await api.config().getEmbeddingModelsForProvider(embeddingProvider);
        setEmbeddingModels(result);
        
        // Set default value if not already set
        if (!form.getValues('embeddingModel') && result.length > 0) {
          form.setValue("embeddingModel", result[0]);
        }
      }
    }
    loadEmbeddingModels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [embeddingProvider]);

  const [advancedOpen, setAdvancedOpen] = useState<boolean>(false);

  const handleSubmit = async (values: DataSetFormSchema) => {
    await onSubmit(values);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)}>
        {disabledFields.length > 0 && <DisabledFieldMessage />}
        <div className="space-y-6">
          <FormField
            control={form.control}
            name="name"
            render={({field}) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input placeholder="Name of the data set" {...field}/>
                </FormControl>
                <FormDescription>
                  This is the name of the data set visible to your users
                </FormDescription>
              </FormItem>
            )}
          />

          <div>
            <Label>Language Model</Label>
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="languageModelProvider"
                render={({field}) => (
                  <FormItem>
                    <FormLabel className="hidden">Language Model Provider</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger disabled={!providersConfig}>
                        <SelectValue placeholder="Loading..."/>
                      </SelectTrigger>
                      <SelectContent>
                        {
                          providersConfig?.languageModelProviders &&
                          <>
                            {providersConfig.languageModelProviders.map((provider) => (
                              <SelectItem key={provider} value={provider}>{provider}</SelectItem>
                            ))}
                          </>
                        }
                      </SelectContent>
                    </Select>
                    <FormDescription>The language model to be used by the agent</FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="languageModel"
                render={({field}) => (
                  <FormItem>
                    <FormLabel className="hidden">Language Model</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger disabled={!languageModelNames}>
                          <SelectValue placeholder="Loading..."/>
                      </SelectTrigger>
                      <SelectContent>
                        {
                          languageModelNames &&
                          <>
                            {languageModelNames.map((modelName) => (
                              <SelectItem key={modelName} value={modelName}>{modelName}</SelectItem>
                            ))}
                          </>
                        }
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />
            </div>
          </div>
        </div>

        <Collapsible className="py-4" open={advancedOpen} onOpenChange={setAdvancedOpen}>
          <CollapsibleTrigger asChild>
            <Button variant="link" className="pl-0">
              {advancedOpen ? <ChevronUpIcon/> : <ChevronDownIcon/>}
              Advanced settings
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="space-y-6">
              <FormField
                control={form.control}
                name="embeddingProvider"
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Embedding Provider</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger disabled={!providersConfig || disabledFields.includes('embeddingProvider')}>
                        <FormControl>
                          <SelectValue placeholder="Select a provider for embeddings"/>
                        </FormControl>
                      </SelectTrigger>
                      <SelectContent>
                        {
                          providersConfig?.embeddingProviders &&
                          <>
                          {providersConfig.embeddingProviders.map((provider) => (
                            <SelectItem key={provider} value={provider}>{provider}</SelectItem>
                          ))}
                          </>
                        }
                      </SelectContent>
                    </Select>
                    <FormDescription>The plugin used to create embeddings</FormDescription>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="embeddingModel"
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Embedding Model</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger disabled={!embeddingModels || disabledFields.includes('embeddingModel')}>
                        <FormControl>
                          <SelectValue placeholder="Select a model for embeddings"/>
                        </FormControl>
                      </SelectTrigger>
                      <SelectContent>
                        {
                          embeddingModels &&
                          <>
                            {embeddingModels.map((modelName) => (
                              <SelectItem key={modelName} value={modelName}>{modelName}</SelectItem>
                            ))}
                          </>
                        }
                      </SelectContent>
                    </Select>
                    <FormDescription>The model provided by the plugin</FormDescription>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="embeddingVectorSize"
                disabled={disabledFields.includes('embeddingVectorSize')}
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Vector Size</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormDescription>The size of the embedding vector to use</FormDescription>
                  </FormItem>
                )}
              />
            </div>
          </CollapsibleContent>
        </Collapsible>
        <Button type="submit">{submitButtonText}</Button>
      </form>
    </Form>
  )
} 
