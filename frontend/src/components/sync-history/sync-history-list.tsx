import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { PaginatedTable } from "@/components/util/paginated-table.tsx";
import { SyncStatus, PaginatedResult } from "@/lib/types.ts";
import { CheckCircle, XCircle } from "lucide-react";

const api = new ApiClient(authenticationProviderInstance);

export function SyncHistoryList() {
  const { dataSetId } = useApplicationContext();

  const loadSyncHistory = async (page: number) => {
    if (dataSetId === null) {
      return;
    }

    return await api.dataSets().getSynchronizations(Number(dataSetId), page);
  };

  return (
    <PaginatedTable<SyncStatus>
      loadItems={loadSyncHistory}
      itemsReloadDependencies={dataSetId}
      noItemsMessage="No sync history found."
      tableHeaders={["Time", "Type", "Status", "Error Message"]}
      tableRow={(item, index) => (
        <TableRow key={index}>
          <TableCell>{new Date(item.timestamp).toLocaleString('en-US')}</TableCell>
          <TableCell>{item.product_source_id ? "Product" : "Document"}</TableCell>
          <TableCell>
            {item.status === "success" ? (
              <CheckCircle className="text-green-500" />
            ) : (
              <XCircle className="text-red-500" />
            )}
          </TableCell>
          <TableCell>{item.error_message || "N/A"}</TableCell>
        </TableRow>
      )}
    />
  );
}