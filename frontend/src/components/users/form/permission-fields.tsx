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
                Controls whether the user is able to sign in.
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
      <FormField
        control={form.control}
        name="isStaff"
        render={({field}) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
            <div className="space-y-0.5">
              <FormLabel className="text-base">
                Staff User
              </FormLabel>
              <FormDescription>
                Staff users can manage data sets and users.
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
