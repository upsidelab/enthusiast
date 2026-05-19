import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ApiClient } from "@/lib/api";
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { DataSet } from "@/lib/types";

const api = new ApiClient(authenticationProviderInstance);

interface DeleteDataSetModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  dataSet: DataSet;
  onConfirm: () => void;
}

export function DeleteDataSetModal({ open, onOpenChange, dataSet, onConfirm }: DeleteDataSetModalProps) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!dataSet.id) return;
    setDeleting(true);
    try {
      await api.dataSets().deleteDataSet(dataSet.id);
      onConfirm();
    } catch (error) {
      console.error("Failed to delete data set:", error);
      alert("Failed to delete data set. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Delete Data Set</DialogTitle>
        </DialogHeader>
        <div className="py-4 space-y-2">
          <p className="text-sm">Are you sure you want to delete <strong>"{dataSet.name}"</strong>?</p>
          <p className="text-sm text-muted-foreground">
            This will also permanently delete all products, documents, sources, agents, conversations, and the eCommerce integration associated with this data set.
          </p>
          <p className="text-sm text-muted-foreground">This action cannot be undone.</p>
        </div>
        <DialogFooter className="flex justify-between">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={deleting}>Cancel</Button>
          <Button variant="destructive" onClick={handleDelete} disabled={deleting}>
            {deleting ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
