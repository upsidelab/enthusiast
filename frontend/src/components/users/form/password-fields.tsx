import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx";
import { Input } from "@/components/ui/input.tsx";
import { UseFormReturn } from "react-hook-form";

export interface PasswordFieldsProps {
  form: UseFormReturn<any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export function PasswordFields({ form }: PasswordFieldsProps) {
  return (
    <>
      <FormField
        control={form.control}
        name="password"
        render={({field}) => (
          <FormItem>
            <FormLabel>Password</FormLabel>
            <FormControl>
              <Input type="password" {...field}/>
            </FormControl>
            <FormDescription>
              Minimum 8 characters
            </FormDescription>
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="confirmPassword"
        render={({field}) => (
          <FormItem>
            <FormLabel>Confirm Password</FormLabel>
            <FormControl>
              <Input type="password" {...field}/>
            </FormControl>
            <FormMessage/>
          </FormItem>
        )}
      />
    </>
  )
}
