import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { useEffect, useState } from "react";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { ApiClient, Conversation } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";

const api = new ApiClient(authenticationProviderInstance);

export function ConversationTable() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();

  const navigateToConversation = (id: number) => {
    navigate(`/ask/chat/${id}`);
  };

  useEffect(() => {
    if (dataSetId === null) {
      return;
    }

    const loadData = async () => {
      const apiConversations = await api.getConversations(dataSetId);
      setConversations(apiConversations);
      setIsLoading(false);
    };

    loadData();
  }, [dataSetId]);

  return (
    <SkeletonLoader skeleton={<Skeleton className="w-full h-[100px]"/>} isLoading={isLoading}>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Time</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {conversations.map((item, index) => (
            <TableRow key={index} onClick={() => navigateToConversation(item.id)} className="cursor-pointer">
              <TableCell>{new Date(item.started_at).toLocaleString('en-US')}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </SkeletonLoader>
  );
}
