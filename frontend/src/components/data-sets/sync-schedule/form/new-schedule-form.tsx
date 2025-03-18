import { Form } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button.tsx";
import { DataSetsFields } from "./data-sets-fields.tsx";
import { DetailsFields } from "./details-fields.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ScheduleFrequencyFields } from "./schedule-frequency-field.tsx";
import { TimePickerField } from "./time-picker-field.tsx";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible.tsx";
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react";
import { useState } from "react";
import { Switch } from "@/components/ui/switch.tsx";

const api = new ApiClient(authenticationProviderInstance);

const formSchema = z.object({
  time: z.string().trim().min(1, { message: "Please select a schedule time." }),
});

type CreateScheduleFormSchema = z.infer<typeof formSchema>;

export interface NewScheduleFormProps {
  onScheduleCreated: () => void;
}

export function NewScheduleForm({ onScheduleCreated }: NewScheduleFormProps) {
  const form = useForm<CreateScheduleFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      time: "",
    }
  });

  const [advancedOpen, setAdvancedOpen] = useState<boolean>(false);
  const [isScheduleEnabled, setIsScheduleEnabled] = useState<boolean>(true);

  const handleSubmit = async (values: CreateScheduleFormSchema) => {
    if (isScheduleEnabled) {
      await api.schedules().createSchedule(values);
      onScheduleCreated();
    }
  };

  return (
    <>
      <div className="flex items-center mb-4">
        <span className="mr-2">Schedule Enabled</span>
        <Switch checked={isScheduleEnabled} onCheckedChange={setIsScheduleEnabled} />
      </div>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <fieldset disabled={!isScheduleEnabled}>
            <TimePickerField form={form} name="time" label="Time" description="Select the time for the schedule." />
            <Collapsible className="py-4" open={advancedOpen} onOpenChange={setAdvancedOpen}>
              <CollapsibleTrigger asChild>
                <Button variant="link" className="pl-0">
                  {advancedOpen ? <ChevronUpIcon/> : <ChevronDownIcon/>}
                  Advanced settings
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <ScheduleFrequencyFields form={form} />
              </CollapsibleContent>
            </Collapsible>
          </fieldset>
          <Button type="submit">Apply</Button>
        </form>
      </Form>
    </>
  );
}