import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";

export interface RevokeTokenDialogProps {
  isOpen: boolean;
  onClose: () => void;
  token: string;
  onCopy: () => void;
}

export function RevokeTokenDialog({ isOpen, onClose, token, onCopy }: RevokeTokenDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Token Revoked</DialogTitle>
          <DialogDescription>
            The token has been revoked successfully. Here is the new token. You will only see this once, so please copy it to a safe place.
          </DialogDescription>
        </DialogHeader>
        <div className="my-4 p-2 border rounded">
          {token}
        </div>
        <DialogFooter>
          <Button onClick={onCopy}>Copy Token</Button>
          <Button variant="default" onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
