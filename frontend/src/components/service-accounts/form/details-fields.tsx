import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx";
import { Input } from "@/components/ui/input.tsx";
import { UseFormReturn } from "react-hook-form";

export interface DetailsFieldsProps {
  form: UseFormReturn<any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export function DetailsFields({ form }: DetailsFieldsProps) {
  return (
    <>
      <FormField
        control={form.control}
        name="name"
        render={({field}) => (
          <FormItem>
            <FormLabel>Name</FormLabel>
            <FormControl>
              <Input placeholder="api-client-name" {...field}/>
            </FormControl>
            <FormMessage  />
            <FormDescription>
              The name used to identify this service account
            </FormDescription>
          </FormItem>
        )}
      />
    </>
  )
}
