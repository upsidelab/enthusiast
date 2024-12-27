import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { CopyToClipboardButton } from "@/components/conversation-view/copy-to-clipboard-button.tsx";
import { Input } from "@/components/ui/input.tsx";

export interface TokenGeneratedModalProps {
  title: string;
  description: string;
  token: string;
  open: boolean;
  onOpenChange: (value: boolean) => void;
}

export function TokenGeneratedModal({ title, description, token, open, onOpenChange }: TokenGeneratedModalProps) {
  const handleCloseClick = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <div className="flex space-x-2 items-center">
          <Input disabled={true} value={token}/>
          <CopyToClipboardButton message={token} variant="default" />
        </div>
        <DialogFooter>
          <Button variant="secondary" onClick={handleCloseClick}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
