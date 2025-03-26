import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx";
import { UseFormReturn } from "react-hook-form";
import { TimePicker } from "@/components/ui/time-picker";

export interface TimePickerFieldProps {
  form: UseFormReturn<any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  name: string;
  label: string;
  description?: string;
}

export function TimePickerField({ form, name, label, description }: TimePickerFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel className="block">{label}</FormLabel>
          <FormControl>
            <TimePicker value={field.value} onChange={field.onChange} />
          </FormControl>
          <FormMessage />
          {description && <FormDescription>{description}</FormDescription>}
        </FormItem>
      )}
    />
  );
}