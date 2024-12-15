import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { User } from "@/lib/api.ts";
import { EditUserForm } from "@/components/users/form/edit-user-form.tsx";

export interface EditUserModalProps {
  user: User;
  onUserUpdated: () => void;
}

export function EditUserModal({ user, onUserUpdated }: EditUserModalProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="secondary">Edit</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit {user.email}</DialogTitle>
        </DialogHeader>
        <EditUserForm user={user} onUserUpdated={onUserUpdated} />
      </DialogContent>
    </Dialog>
  )
}
