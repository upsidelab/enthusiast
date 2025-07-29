import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { Agent } from "@/lib/types";

const apiClient = new ApiClient(authenticationProviderInstance);

interface DeleteConfirmationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  agent: Agent | null;
  onConfirm: () => void;
}

export function DeleteConfirmationModal({ 
  open, 
  onOpenChange, 
  agent, 
  onConfirm 
}: DeleteConfirmationModalProps) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!agent) return;

    setDeleting(true);
    try {
      await apiClient.agents().deleteAgent(agent.id);
      onConfirm();
    } catch (error: any) {
      console.error('Failed to delete agent:', error);
      alert('Failed to delete agent. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Confirm Deletion</DialogTitle>
        </DialogHeader>
        <div className="py-4">
          <p className="text-sm mb-2">Are you sure you want to delete agent "{agent?.name}"?</p>
          <p className="text-sm">This action cannot be undone.</p>
        </div>
        <DialogFooter className="flex justify-between">
          <Button variant="outline" onClick={handleCancel} disabled={deleting}>Cancel</Button>
          <Button variant="destructive" onClick={handleDelete} disabled={deleting}>
            {deleting ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
