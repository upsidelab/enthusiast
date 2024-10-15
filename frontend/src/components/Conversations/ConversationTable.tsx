import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { useEffect, useState } from "react";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { ApiClient, Conversation } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";

const api = new ApiClient(authenticationProviderInstance);

export function ConversationTable() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { dataSetId } = useApplicationContext()!;

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
        <TableCaption>Sync Status: Manual</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>When</TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Dimensions</TableHead>
            <TableHead>Data Set</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {conversations.map((item, index) => (
            <TableRow key={index}>
              <TableCell>{new Date(item.started_at).toLocaleString(undefined, {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false,
                })}
              </TableCell>
              <TableCell>{item.model}</TableCell>
              <TableCell>{item.dimensions}</TableCell>
              <TableCell>{item.data_set}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </SkeletonLoader>
  );
}
