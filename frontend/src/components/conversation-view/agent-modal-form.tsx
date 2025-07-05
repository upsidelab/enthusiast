import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button.tsx";
import { useEffect, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

import {AvailableAgents} from "@/lib/types.ts";

const formSchema = z.object({
  agent: z.string()
});

type CreateDataSetFormSchema = z.infer<typeof formSchema>;
export interface AgentSelectionFormProps {
  currentAgent: string;
  onSubmit: (selectedAgent: string) => void;
}

const api = new ApiClient(authenticationProviderInstance);

export function AgentSelectionForm({
  currentAgent,
  onSubmit,
}: AgentSelectionFormProps) {
    const form = useForm<CreateDataSetFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agent: currentAgent,
    }
  });
  const [availableAgents, setAvailableAgents] = useState<AvailableAgents>({choices: []});
  const handleSubmit = async (values: CreateDataSetFormSchema) => {
      onSubmit(values.agent);
  };
  const fetchAgents = async () => {
            const availableAgentsResponse = await api.conversations().getAvailableAgents()
            setAvailableAgents(availableAgentsResponse)
        }

  useEffect(() => {
    fetchAgents()
    }, []);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <div className="space-y-6">
              <FormField
                control={form.control}
                name="agent"
                render={({field}) => (
                  <FormItem>
                    <FormLabel>Available Agents</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger>
                        <FormControl>
                          <SelectValue placeholder="Select an Agent"/>
                        </FormControl>
                      </SelectTrigger>
                        <SelectContent>
                          {availableAgents.choices.map((agent) => (
                            <SelectItem key={agent} value={agent}>
                              {agent}
                            </SelectItem>
                          ))}
                        </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />
            </div>
        <Button type="submit">Confirm</Button>
      </form>
    </Form>
  )
}
