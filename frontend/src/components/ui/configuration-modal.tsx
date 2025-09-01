import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ReactNode } from "react";

interface ConfigurationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  children: ReactNode;
  onSubmit: () => void;
  onCancel: () => void;
  submitLabel: string;
  cancelLabel?: string;
  submitting: boolean;
  disabled?: boolean;
  loading?: boolean;
  loadingText?: string;
}

export function ConfigurationModal({
  open,
  onOpenChange,
  title,
  children,
  onSubmit,
  onCancel,
  submitLabel,
  cancelLabel = "Cancel",
  submitting,
  disabled = false,
  loading = false,
  loadingText = "Loading..."
}: ConfigurationModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <p className="text-muted-foreground">{loadingText}</p>
          </div>
        ) : (
          <div className="space-y-6">
            {children}
          </div>
        )}
        
        <DialogFooter className="flex-shrink-0">
          <Button onClick={onCancel} disabled={submitting}>
            {cancelLabel}
          </Button>
          <Button disabled={disabled || submitting} onClick={onSubmit}>
            {submitting ? "Saving..." : submitLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
