import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useState } from "react";
import { EditServiceAccountForm } from "@/components/service-accounts/form/edit-service-account-form.tsx";
import { ServiceAccount } from "@/lib/types.ts";

export interface NewServiceAccountModalProps {
  serviceAccount: ServiceAccount;
  onServiceAccountUpdated: () => void;
}

export function EditServiceAccountModal({ serviceAccount, onServiceAccountUpdated }: NewServiceAccountModalProps) {
  const [open, setOpen] = useState(false);
  const handleServiceAccountUpdated = () => {
    setOpen(false);
    onServiceAccountUpdated();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary">Edit</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New Service Account</DialogTitle>
        </DialogHeader>
        <EditServiceAccountForm serviceAccount={serviceAccount} onServiceAccountUpdated={handleServiceAccountUpdated} />
      </DialogContent>
    </Dialog>
  );
}
