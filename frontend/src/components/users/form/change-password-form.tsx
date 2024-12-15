import { Form } from "@/components/ui/form.tsx";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { ApiClient, User } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Button } from "@/components/ui/button.tsx";
import { PasswordFields } from "@/components/users/form/password-fields.tsx";

const formSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
});

type UserFormSchema = z.infer<typeof formSchema>;
const api = new ApiClient(authenticationProviderInstance);

export interface ChangePasswordFormProps {
  user: User;
  onUserUpdated: () => void;
}

export function ChangePasswordForm({ user, onUserUpdated }: ChangePasswordFormProps) {
  const form = useForm<UserFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      password: '',
      confirmPassword: ''
    }
  });

  const handleSubmit = async (values: UserFormSchema) => {
    await api.users().updateUserPassword(user.id, values.password);
    onUserUpdated();
    form.reset();
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <PasswordFields form={form} />
        <Button type="submit">Change Password</Button>
      </form>
    </Form>
  )
}
