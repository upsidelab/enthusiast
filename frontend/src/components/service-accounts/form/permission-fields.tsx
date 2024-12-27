import { FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { Switch } from "@/components/ui/switch.tsx";
import { UseFormReturn } from "react-hook-form";

export interface PermissionFieldsProps {
  form: UseFormReturn<any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export function PermissionFields({ form }: PermissionFieldsProps) {
  return (
    <>
      <h3 className="mb-4 text-lg font-medium">Permissions</h3>
      <FormField
        control={form.control}
        name="isActive"
        render={({field}) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
            <div className="space-y-0.5">
              <FormLabel className="text-base">
                Active
              </FormLabel>
              <FormDescription>
                Controls whether the service account is able to use the API.
              </FormDescription>
            </div>
            <FormControl>
              <Switch
                checked={field.value}
                onCheckedChange={field.onChange}
              />
            </FormControl>
          </FormItem>
        )}
      />
    </>
  )
}
