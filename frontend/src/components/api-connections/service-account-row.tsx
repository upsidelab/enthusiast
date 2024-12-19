import { Button } from "@/components/ui/button.tsx";
import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { EditIcon, TrashIcon, KeyIcon } from "lucide-react";
import { ServiceAccount } from "@/lib/types.ts";

export interface ServiceAccountRowProps {
  serviceAccount: ServiceAccount;
  onEdit: (e: ServiceAccount) => void;
  onDeactivate: (e: ServiceAccount) => void;
  onRevokeToken: (e: ServiceAccount) => void;
}

export function ServiceAccountRow({ serviceAccount, onEdit, onDeactivate, onRevokeToken }: ServiceAccountRowProps) {
  return (
    <TableRow>
      <TableCell>{serviceAccount.email.split('@')[0]}</TableCell>
      <TableCell>{new Date(serviceAccount.date_joined).toLocaleDateString()}</TableCell>
      <TableCell>{serviceAccount.data_sets?.join(", ") || "No datasets"}</TableCell>
      <TableCell className="flex space-x-2">
        <Button variant="outline" onClick={() => onEdit(serviceAccount)}>
          <EditIcon className="h-4 w-4" />
        </Button>
        <Button variant="destructive" onClick={() => onDeactivate(serviceAccount)}>
          <TrashIcon className="h-4 w-4" />
        </Button>
        <Button variant="default" onClick={() => onRevokeToken(serviceAccount)}>
          <KeyIcon className="h-4 w-4" />
        </Button>
      </TableCell>
    </TableRow>
  );
}
