import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { User } from "@/lib/api.ts";
import { ChangePasswordForm } from "@/components/users/form/change-password-form.tsx";

export interface ChangePasswordModalProps {
  user: User;
  onUserUpdated: () => void;
}

export function ChangePasswordModal({ user, onUserUpdated }: ChangePasswordModalProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="secondary">Change Password</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Change Password for {user.email}</DialogTitle>
        </DialogHeader>
        <ChangePasswordForm user={user} onUserUpdated={onUserUpdated} />
      </DialogContent>
    </Dialog>
  )
}
