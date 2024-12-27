import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { NewServiceAccountForm } from "@/components/service-accounts/form/new-service-account-form.tsx";
import { useState } from "react";

export interface NewServiceAccountModalProps {
  onServiceAccountCreated: () => void;
}

export function NewServiceAccountModal({ onServiceAccountCreated }: NewServiceAccountModalProps) {
  const [open, setOpen] = useState(false);
  const handleServiceAccountCreated = () => {
    setOpen(false);
    onServiceAccountCreated();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="default">New Service Account</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New Service Account</DialogTitle>
        </DialogHeader>
        <NewServiceAccountForm onServiceAccountCreated={handleServiceAccountCreated} />
      </DialogContent>
    </Dialog>
  );
}
