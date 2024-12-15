import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { NewUserForm } from "@/components/users/form/new-user-form.tsx";

export interface NewUserModalProps {
  onUserCreated: () => void;
}

export function NewUserModal({ onUserCreated }: NewUserModalProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="default">New User</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New User</DialogTitle>
        </DialogHeader>
        <NewUserForm onUserCreated={onUserCreated} />
      </DialogContent>
    </Dialog>
  )
}
