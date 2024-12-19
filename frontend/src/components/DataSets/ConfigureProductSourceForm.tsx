import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useCallback, useEffect, useState } from 'react';
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Textarea } from "@/components/ui/textarea.tsx"
import { Button } from "@/components/ui/button.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ProductSource } from "@/lib/types.ts";

const formSchema = z.object({
  id: z.number().min(1),
  config: z.string().min(1),
  data_set_id: z.number().min(1),
});

type ConfigureProductSourceFormSchema = z.infer<typeof formSchema>;
const api = new ApiClient(authenticationProviderInstance);

export interface DataSetProductSourceProps {
  dataSetId: number;
  productSourceId: number;
}

export function ConfigureProductSourceForm({ dataSetId, productSourceId }: DataSetProductSourceProps) {
  const [productSource, setProductSource] = useState<ProductSource>();

  const fetchProductSource = useCallback(async () => {
    const response = await api.dataSets().getDataSetProductSource(dataSetId, productSourceId);
    setProductSource(response);
  }, [dataSetId, productSourceId]);

  useEffect(() => {
    fetchProductSource();
  }, [fetchProductSource, dataSetId, productSourceId]);

  const form = useForm<ConfigureProductSourceFormSchema>({
    resolver: zodResolver(formSchema),
  });

  const { reset } = form;

  useEffect(() => {
    if (productSource) {
      reset({
        id: productSource.id,
        data_set_id: productSource.data_set_id,
        config: productSource.config,
      });
    }
  }, [productSource, reset]);

  const handleSubmit = async (values: ConfigureProductSourceFormSchema) => {
    await api.dataSets().configureDataSetProductSource(values as ProductSource);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)}>
        <FormField
          control={form.control}
          name="config"
          render={({field}) => (
            <FormItem>
              <FormLabel>Product Source Config</FormLabel>
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
