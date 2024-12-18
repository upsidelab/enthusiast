import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog.tsx";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ServiceAccount } from "@/lib/types.ts";

const formSchema = z.object({
  name: z.string().trim().min(1, "Name is required")
});

export interface EditServiceAccountDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (values: { name: string }) => void;
  serviceAccount: ServiceAccount | null;
  errorMessage: string | null;
}

export function EditServiceAccountDialog({ isOpen, onClose, onSubmit, serviceAccount, errorMessage }: EditServiceAccountDialogProps) {
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: serviceAccount?.email?.split('@')[0] || ""
    }
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Service Account Name</DialogTitle>
          <DialogDescription>
            Update the name of the service account.
          </DialogDescription>
        </DialogHeader>
        {errorMessage && <div className="text-red-500 mb-4">{errorMessage}</div>}
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor="name">Name</FormLabel>
                  <FormControl>
                    <Input id="name" {...field} autoComplete="name" />
                  </FormControl>
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="submit">Save</Button>
              <Button variant="default" onClick={onClose}>Cancel</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
