import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible.tsx";
import { useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react";
import { ApiClient, DataSet } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useNavigate } from "react-router-dom";
import { useApplicationContext } from "@/lib/use-application-context.ts";

const formSchema = z.object({
  name: z.string().trim().min(1),
  embeddingProvider: z.string().min(1),
  embeddingModel: z.string().min(1),
  embeddingVectorSize: z.number().min(1).max(3072)
});

type CreateDataSetFormSchema = z.infer<typeof formSchema>;
const api = new ApiClient(authenticationProviderInstance);

export function CreateDataSetForm() {
  const { setDataSets, setDataSetId } = useApplicationContext()!;
  const form = useForm<CreateDataSetFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      embeddingProvider: "OpenAI",
      embeddingModel: "text-embedding-3-large",
      embeddingVectorSize: 512,
    }
  });

  const [advancedOpen, setAdvancedOpen] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleSubmit = async (values: CreateDataSetFormSchema) => {
    const createdDataSetId = await api.dataSets().createDataSet(values as DataSet);
    const dataSets = await api.dataSets().getDataSets();
    setDataSets(dataSets);
    setDataSetId(createdDataSetId);
    navigate(`/data-sets/${createdDataSetId}/users`);
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
                name="embeddingProvider"
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Provider</FormLabel>
                    <Select {...field}>
                      <SelectTrigger>
                        <FormControl>
                          <SelectValue placeholder="Select a provider for embeddings"/>
                        </FormControl>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="OpenAI">OpenAI</SelectItem>
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
                    <FormLabel>Model</FormLabel>
                    <Select {...field}>
                      <SelectTrigger>
                        <FormControl>
                          <SelectValue placeholder="Select a model for embeddings"/>
                        </FormControl>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="text-embedding-3-large">text-embedding-3-large</SelectItem>
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
            </div>
          </CollapsibleContent>
        </Collapsible>
        <Button type="submit">Create</Button>
      </form>
    </Form>
  )
}
