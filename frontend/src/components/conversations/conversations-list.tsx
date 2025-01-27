import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import { PaginatedTable } from "@/components/util/paginated-table.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function ConversationsList() {
  const { dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();

  const navigateToConversation = (id: number) => {
    navigate(`/data-sets/${dataSetId}/chat/${id}`);
  };

  const loadConversations = async (page: number) => {
    if (dataSetId === null) {
      return;
    }

    return await api.conversations().getConversations(dataSetId, page);
  }

  const truncateText = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength - 3) + '...';
  }

  return (
    <PaginatedTable
      loadItems={loadConversations}
      itemsReloadDependencies={dataSetId}
      noItemsMessage="You don't have any conversations yet"
      tableHeaders={["Name", "Time"]}
      tableRow={(item, index) => {
        return (
          <TableRow key={index} onClick={() => navigateToConversation(item.id)} className="cursor-pointer">
            <TableCell>{truncateText(item.summary || "Unnamed Conversation", 180)}</TableCell>
            <TableCell>{new Date(item.started_at).toLocaleString('en-US')}</TableCell>
          </TableRow>
        )
      }}
    />
  );
}
