import { FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
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
        name="email"
        render={({field}) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input placeholder="user@example.com" {...field}/>
            </FormControl>
            <FormDescription>
              The email address used to sign in to the application
            </FormDescription>
          </FormItem>
        )}
      />
    </>
  )
}
