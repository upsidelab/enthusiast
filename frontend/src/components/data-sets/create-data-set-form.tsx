import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { z } from "zod";
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
import { useNavigate } from "react-router-dom";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { DataSet, ProvidersConfig } from "@/lib/types.ts";

const formSchema = z.object({
  name: z.string().trim().min(1),
  languageModelProvider: z.string().min(1),
  languageModel: z.string().min(1),
  embeddingProvider: z.string().min(1),
  embeddingModel: z.string().min(1),
  embeddingVectorSize: z.number().min(1).max(3072),
  systemMessage: z.string().min(1)
});

type CreateDataSetFormSchema = z.infer<typeof formSchema>;
const api = new ApiClient(authenticationProviderInstance);

export function CreateDataSetForm() {
  const { setDataSets, setDataSetId } = useApplicationContext()!;
  const [providersConfig, setProvidersConfig] = useState<ProvidersConfig | undefined>(undefined);
  const [languageModelNames, setLanguageModelNames] = useState<string[] | undefined>(undefined);
  const [embeddingModels, setEmbeddingModels] = useState<string[] | undefined>(undefined);

  const form = useForm<CreateDataSetFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      languageModelProvider: undefined,
      languageModel: undefined,
      embeddingProvider: undefined,
      embeddingModel: undefined,
      embeddingVectorSize: 512,
      systemMessage: "You are a sales support agent, and you know everything about a company and their products."
    }
  });

  useEffect(() => {
    const loadProvidersConfig = async () => {
      const result = await api.config().getAvailableProviders();
      setProvidersConfig(result);
      form.setValue("languageModelProvider", result.languageModelProviders[0], {});
      form.setValue("embeddingProvider", result.embeddingProviders[0], {});
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
        form.setValue("languageModel", result[0], {});
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
        form.setValue("embeddingModel", result[0], {});
      }
    }
    loadEmbeddingModels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [embeddingProvider]);

  const [advancedOpen, setAdvancedOpen] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleSubmit = async (values: CreateDataSetFormSchema) => {
    const createdDataSetId = await api.dataSets().createDataSet({ ...values, id: undefined } as DataSet);
    const dataSets = await api.dataSets().getDataSets();
    setDataSets(dataSets);
    setDataSetId(createdDataSetId);
    navigate(`/data-sets/${createdDataSetId}/catalog-sources`);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)}>
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
                disabled={!providersConfig}
                name="languageModelProvider"
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Language Model Provider</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger>
                        <FormControl>
                          <SelectValue placeholder="Select a language model provider"/>
                        </FormControl>
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
                    <FormDescription>The plugin used to provide a language model</FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="languageModel"
                disabled={!languageModelNames}
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Language Model</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger>
                        <FormControl>
                          <SelectValue placeholder="Select a language model to use"/>
                        </FormControl>
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
                    <FormDescription>The language model to be used by the agent</FormDescription>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="embeddingProvider"
                disabled={!providersConfig}
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Embedding Provider</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger>
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
                disabled={!embeddingModels}
                name="embeddingModel"
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Embedding Model</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger>
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
              <FormField
                control={form.control}
                name="systemMessage"
                render={({field}) => (
                  <FormItem>
                    <FormLabel>System Message</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormDescription>
                      This message will be used by the agent as the system prompt.
                    </FormDescription>
                  </FormItem>
                )}
              />
            </div>
          </CollapsibleContent>
        </Collapsible>
        <Button type="submit">Create</Button>
      </form>
    </Form>
  )
}
