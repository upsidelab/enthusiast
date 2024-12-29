import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useCallback, useEffect, useState } from 'react';
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Textarea } from "@/components/ui/textarea.tsx"
import { Button } from "@/components/ui/button.tsx";
import { CatalogSource } from "@/lib/types.ts";

const formSchema = z.object({
  id: z.number().min(1),
  config: z.string().min(1),
  data_set_id: z.number().min(1),
});

type ConfigureDataSetSourceFormSchema = z.infer<typeof formSchema>;

export interface ConfigureDataSetSourceProps {
  dataSetId: number;
  sourceId: number;
  getDataSetSource: (dataSetId: number, sourceId: number) => Promise<CatalogSource>;
  configureDataSetSource: (source: CatalogSource) => Promise<number>;
}

export function ConfigureDataSetSourceForm({ dataSetId, sourceId, getDataSetSource, configureDataSetSource }: ConfigureDataSetSourceProps) {
  const [source, setSource] = useState<CatalogSource>();

  const fetchSource = useCallback(async () => {
    const response = await getDataSetSource(dataSetId, sourceId);
    setSource(response);
  }, [dataSetId, sourceId, getDataSetSource]);

  useEffect(() => {
    fetchSource();
  }, [fetchSource, dataSetId, sourceId]);

  const form = useForm<ConfigureDataSetSourceFormSchema>({
    resolver: zodResolver(formSchema),
  });

  const { reset } = form;

  useEffect(() => {
    if (source) {
      reset({
        id: source.id,
        data_set_id: source.data_set_id,
        config: JSON.stringify(source.config),
      });
    }
  }, [source, reset]);

  const handleSubmit = async (values: ConfigureDataSetSourceFormSchema) => {
    await configureDataSetSource(values as CatalogSource);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)}>
        <FormField
          control={form.control}
          name="config"
          render={({field}) => (
            <FormItem>
              <FormLabel>Source Config</FormLabel>
              <FormControl>
                <Textarea placeholder="Your plugin config" {...field}/>
              </FormControl>
              <FormDescription>
                Provide parameters requied by your plugin, for details please consult documentation.
              </FormDescription>
            </FormItem>
          )}
        />
        <Button type="submit">Save</Button>
      </form>
    </Form>
  )
}
