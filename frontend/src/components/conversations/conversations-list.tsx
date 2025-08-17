import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import { PaginatedTable } from "@/components/util/paginated-table.tsx";
import { Lock } from "lucide-react";

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
      tableHeaders={["Conversation", "Agent", "Time"]}
      tableRow={(item, index) => {
        const isAgentDeleted = !!item.agent.deleted_at;
        const isAgentCorrupted = !!item.agent.corrupted;
        return (
          <TableRow key={index} onClick={() => navigateToConversation(item.id)} className="cursor-pointer">
            <TableCell>
              <div className="flex items-center gap-2">
                {(isAgentDeleted || isAgentCorrupted) && <Lock className="h-4 w-4 text-muted-foreground" />}
                <span className={isAgentDeleted || isAgentCorrupted ? "text-muted-foreground" : ""}>
                  {truncateText(item.summary || "Unnamed Conversation", 180)}
                </span>
              </div>
            </TableCell>
            <TableCell className="w-1/4">
              {item.agent.name}
            </TableCell>
            <TableCell className="w-1/4">{new Date(item.started_at).toLocaleString('en-US')}</TableCell>
          </TableRow>
        )
      }}
    />
  );
}
