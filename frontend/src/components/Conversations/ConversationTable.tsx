import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { useEffect, useState } from "react";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { ApiClient, Conversation } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import RenderPaginationItems from "@/components/util/PaginationUtils.tsx";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const api = new ApiClient(authenticationProviderInstance);

export function ConversationTable() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalConversations, setTotalConversations] = useState(0);
  const itemsPerPage = 25;
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
      setIsLoading(true);
        const apiConversations = await api.getConversations(dataSetId, currentPage);
        setConversations(apiConversations.results);
        setTotalConversations(apiConversations.count);
        setIsLoading(false);
    };

    loadData();
  }, [dataSetId, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const totalPages = Math.ceil(totalConversations / itemsPerPage);

  return (
    <SkeletonLoader skeleton={<Skeleton className="w-full h-[100px]" />} isLoading={isLoading}>
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
      {!isLoading && (
        <Pagination className="my-4 text-lg">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                href="#"
                onClick={() => handlePageChange(Math.max(currentPage - 1, 1))}
              />
            </PaginationItem>
              <RenderPaginationItems
                currentPage={currentPage}
                totalPages={totalPages}
                handlePageChange={handlePageChange}
              />
            <PaginationItem>
              <PaginationNext
                href="#"
                onClick={() => handlePageChange(Math.min(currentPage + 1, totalPages))}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </SkeletonLoader>
  );
}