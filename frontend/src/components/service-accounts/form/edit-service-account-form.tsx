import { useEffect } from "react";
import { Form } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button.tsx";
import { checkServiceNameAvailability } from "@/components/util/check-service-name-availability.tsx";
import { DetailsFields } from "@/components/service-accounts/form/details-fields.tsx";
import { DataSetsFields } from "@/components/service-accounts/form/data-sets-fields.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ServiceAccount } from "@/lib/types.ts";
import { PermissionFields } from "@/components/service-accounts/form/permission-fields.tsx";

const api = new ApiClient(authenticationProviderInstance);

const formSchema = z.object({
  oldName: z.string().trim(),
  name: z.string().trim().min(1),
  dataSetIds: z.array(z.number()),
  isActive: z.boolean(),
  isStaff: z.boolean(),
}).refine(async (data) => data.name === data.oldName || await checkServiceNameAvailability(data.name), {
  message: "The name has already been taken",
  path: ["name"],
});

type CreateServiceAccountFormSchema = z.infer<typeof formSchema>;

export interface EditServiceAccountFormProps {
  serviceAccount: ServiceAccount;
  onServiceAccountUpdated: () => void;
}

export function EditServiceAccountForm({ serviceAccount, onServiceAccountUpdated }: EditServiceAccountFormProps) {
  const oldName = serviceAccount.email.split('@')[0];
  const form = useForm<CreateServiceAccountFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: oldName,
      oldName: oldName,
      dataSetIds: serviceAccount.dataSetIds || [],
      isActive: serviceAccount.isActive,
      isStaff: serviceAccount.isStaff || false,
    }
  });
  const isStaff = useWatch({ control: form.control, name: "isStaff" });

  useEffect(() => {
    if (isStaff) {
      form.setValue("dataSetIds", []);
    }
  }, [isStaff, form]);

  const handleSubmit = async (values: CreateServiceAccountFormSchema) => {
    await api.serviceAccounts().updateServiceAccount(serviceAccount.id, values);
    onServiceAccountUpdated();
  };

  return (
    <>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <DetailsFields form={form}/>
          <PermissionFields form={form}/>
          {!isStaff && <DataSetsFields form={form}/>}
          <Button type="submit">Update</Button>
        </form>
      </Form>
    </>
  );
}
