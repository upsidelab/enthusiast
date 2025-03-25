import { Form } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button.tsx";
import { TimePickerField } from "./time-picker-field.tsx";
import { ScheduleFrequencyFields } from "./schedule-frequency-field.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible.tsx";
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { Switch } from "@/components/ui/switch.tsx";
import { toast } from "sonner";

const api = new ApiClient(authenticationProviderInstance);

const formSchema = (isScheduleEnabled: boolean) => z.object({
  time: isScheduleEnabled ? z.string().trim().min(1, { message: "Please select a schedule time." }) : z.string().optional(),
  frequency: z.string().optional(),
  day_of_week: z.string().optional(),
  enabled: z.boolean(),
});

type CreateScheduleFormSchema = z.infer<ReturnType<typeof formSchema>>;

export interface NewScheduleFormProps {
  dataSetId: number;
  onScheduleCreated: () => void;
  initialValues: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export function NewScheduleForm({ dataSetId, onScheduleCreated, initialValues }: NewScheduleFormProps) {
  const [isScheduleEnabled, setIsScheduleEnabled] = useState<boolean>(false);
  const resetDone = useRef(false);

  const form = useForm<CreateScheduleFormSchema>({
    resolver: zodResolver(formSchema(isScheduleEnabled)),
    defaultValues: {
      time: initialValues?.time || "",
      frequency: initialValues?.frequency || "weekly",
      day_of_week: initialValues?.day_of_week || "sun",
      enabled: initialValues?.enabled || false,
    }
  });

  const [advancedOpen, setAdvancedOpen] = useState<boolean>(false);

  useEffect(() => {
    if (initialValues && !resetDone.current) {
      form.reset(initialValues);
      setIsScheduleEnabled(initialValues.enabled);
      resetDone.current = true;
    }
  }, [initialValues, form]);

  const handleSubmit = async (values: CreateScheduleFormSchema) => {
    const payload = {
      ...values,
      enabled: isScheduleEnabled,
    };
    await api.dataSets().createSyncSchedule(dataSetId, payload);
    toast.success("Sync schedule applied successfully.");
    onScheduleCreated();
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
