import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { PaginatedTable } from "@/components/util/paginated-table.tsx";
import { SyncStatus, PaginatedResult } from "@/lib/types.ts";
import { CheckCircle, XCircle } from "lucide-react";
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function SyncHistoryList() {
  const { dataSetId } = useApplicationContext();
  const [errorDialogOpen, setErrorDialogOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const loadSyncHistory = async (page: number) => {
    if (dataSetId === null) {
      return;
    }

    return await api.dataSets().getSynchronizations(Number(dataSetId), page);
  };

  const handleShowErrorDetails = (message: string) => {
    setErrorMessage(message);
    setErrorDialogOpen(true);
  };

  return (
    <>
      <PaginatedTable<SyncStatus>
        loadItems={loadSyncHistory}
        itemsReloadDependencies={dataSetId}
        noItemsMessage="No sync history found."
        tableHeaders={["Time", "Type", "Status"]}
        tableRow={(item, index) => (
          <TableRow key={index}>
            <TableCell>{new Date(item.timestamp).toLocaleString('en-US')}</TableCell>
            <TableCell>{item.product_source_id ? "Product" : "Document"}</TableCell>
            <TableCell className="flex items-center">
              {item.status === "success" ? (
                <CheckCircle className="text-green-500" />
              ) : (
                <div className="flex items-center">
                  <XCircle className="text-red-500" />
                  <Button
                    variant="link"
                    onClick={() => handleShowErrorDetails(item.error_message || "Unknown error")}
                    aria-label="Show Details"
                    className="ml-2 p-0"
                  >
                    Show Details
                  </Button>
                </div>
              )}
            </TableCell>
          </TableRow>
        )}
      />
      <Dialog open={errorDialogOpen} onOpenChange={setErrorDialogOpen}>
        <DialogContent className="max-w-lg p-6">
          <DialogHeader>
            <DialogTitle>Error Details</DialogTitle>
          </DialogHeader>
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            {errorMessage}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
