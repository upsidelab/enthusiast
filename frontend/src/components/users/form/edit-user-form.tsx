import { Form } from "@/components/ui/form.tsx";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { ApiClient, User } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Button } from "@/components/ui/button.tsx";
import { PermissionFields } from "@/components/users/form/permission-fields.tsx";
import { DetailsFields } from "@/components/users/form/details-fields.tsx";

const formSchema = z.object({
  email: z.string().trim().email(),
  isActive: z.boolean(),
  isStaff: z.boolean(),
});

type UserFormSchema = z.infer<typeof formSchema>;
const api = new ApiClient(authenticationProviderInstance);

export interface EditUserFormProps {
  user: User;
  onUserUpdated: () => void;
}

export function EditUserForm({ user, onUserUpdated }: EditUserFormProps) {
  const form = useForm<UserFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: user.email,
      isActive: user.isActive,
      isStaff: user.isStaff
    }
  });

  const handleSubmit = async (values: UserFormSchema) => {
    await api.users().updateUser(user.id, values);
    onUserUpdated();
    form.reset();
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <DetailsFields form={form} />
        <PermissionFields form={form} />
        <Button type="submit">Update</Button>
      </form>
    </Form>
  )
}
