import { useState, useEffect } from "react";
import { Form } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useWatch } from "react-hook-form";
import { Button } from "@/components/ui/button.tsx";
import { checkServiceNameAvailability } from "@/components/util/check-service-name-availability.tsx";
import { TokenGeneratedModal } from "@/components/service-accounts/token-generated-modal.tsx";
import { DetailsFields } from "@/components/service-accounts/form/details-fields.tsx";
import { DataSetsFields } from "@/components/service-accounts/form/data-sets-fields.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { PermissionFields } from "@/components/service-accounts/form/permission-fields.tsx";

const api = new ApiClient(authenticationProviderInstance);

const formSchema = z.object({
  name: z.string().trim().min(1).refine(async (name) => {
    return await checkServiceNameAvailability(name);
  }, {
    message: "The name has already been taken"
  }),
  dataSetIds: z.array(z.number()),
  isActive: z.boolean(),
  isStaff: z.boolean(),
});
type CreateServiceAccountFormSchema = z.infer<typeof formSchema>;

export interface NewServiceAccountFormProps {
  onServiceAccountCreated: () => void;
}

export function NewServiceAccountForm({onServiceAccountCreated}: NewServiceAccountFormProps) {
  const form = useForm<CreateServiceAccountFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      dataSetIds: [],
      isActive: true,
      isStaff: false,
    }
  });
  const [isTokenDialogOpen, setIsTokenDialogOpen] = useState(false);
  const [generatedToken, setGeneratedToken] = useState("");
  const isStaff = useWatch({ control: form.control, name: "isStaff" });

  useEffect(() => {
    if (isStaff) {
      form.setValue("dataSetIds", []);
    }
  }, [isStaff, form]);

  const handleSubmit = async (values: CreateServiceAccountFormSchema) => {
    const {  token } = await api.serviceAccounts().createServiceAccount(values);
    setGeneratedToken(token);
    setIsTokenDialogOpen(true);
  };

  const handleTokenDialogOpenChange = (value: boolean) => {
    setIsTokenDialogOpen(value);
    if (!value) {
      onServiceAccountCreated();
    }
  };

  return (
    <>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <DetailsFields form={form}/>
          <PermissionFields form={form}/>
          {!isStaff && <DataSetsFields form={form}/>}
          <Button type="submit">Create</Button>
        </form>
      </Form>
      <TokenGeneratedModal
        title="Service Account Created"
        description="To access the API using this account, use the token provided below. You will only see this token once, so please store it in a safe place."
        token={generatedToken}
        open={isTokenDialogOpen}
        onOpenChange={handleTokenDialogOpenChange}
      />
    </>
  );
}
