import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import { PaginatedTable } from "@/components/util/PaginatedTable.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function ConversationTable() {
  const { dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();

  const navigateToConversation = (id: number) => {
    navigate(`/ask/chat/${id}`);
  };

  const loadConversations = async (page: number) => {
    if (dataSetId === null) {
      return;
    }

    return await api.conversations().getConversations(dataSetId, page);
  }

  return (
    <PaginatedTable
      loadItems={loadConversations}
      itemsReloadDependencies={dataSetId}
      noItemsMessage="You don't have any conversations yet"
      tableHeaders={["Time"]}
      tableRow={(item, index) => {
        return (
          <TableRow key={index} onClick={() => navigateToConversation(item.id)} className="cursor-pointer">
            <TableCell>{new Date(item.started_at).toLocaleString('en-US')}</TableCell>
          </TableRow>
        )
      }}
    />
  );
}
