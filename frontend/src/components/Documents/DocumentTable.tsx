import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { useEffect, useState } from "react";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { ApiClient, Document } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ScrollArea } from "@/components/ui/scroll-area.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import RenderPaginationItems from "@/components/util/PaginationUtils.tsx";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const api = new ApiClient(authenticationProviderInstance);

export function DocumentTable() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalDocuments, setTotalDocuments] = useState(0);
  const itemsPerPage = 25;
  const { dataSetId } = useApplicationContext()!;
  const [selectedPreview, setSelectedPreview] = useState<Document | null>(null);

  const extractSlug = (url: string) => {
    if (!URL.canParse(url)) {
      return url;
    }

    return new URL(url).pathname;
  };

  useEffect(() => {
    if (dataSetId === null) {
      return;
    }

    const loadData = async () => {
      const response = await api.getDocuments(dataSetId, currentPage);
      setDocuments(response.results);
      setTotalDocuments(response.count);
      setSelectedPreview(null);
      setIsLoading(false);
    };

    loadData();
  }, [dataSetId, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const totalPages = Math.ceil(totalDocuments / itemsPerPage);

  if (documents.length === 0 && !isLoading) {
    return (
      <div className="text-center">
        <h2 className="font-bold">No documents available</h2>
      </div>
    );
  }

  return (
    <SkeletonLoader skeleton={<Skeleton className="w-full h-[100px]" />} isLoading={isLoading}>
      <Table>
        <TableCaption>Sync Status: Manual</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>URL</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Content</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((item, index) => (
            <TableRow key={index}>
              <TableCell>
                <Button variant="link" asChild>
                  <a href={item.url} target="_blank">{extractSlug(item.url)}</a>
                </Button>
              </TableCell>
              <TableCell>{item.title}</TableCell>
              <TableCell>
                <Button onClick={() => setSelectedPreview(item)}>Show</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Sheet open={!!selectedPreview} onOpenChange={() => setSelectedPreview(null)}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Preview {selectedPreview?.title}</SheetTitle>
          </SheetHeader>
          <ScrollArea className="h-full w-full pt-4">
            <div>
              {selectedPreview?.content}
            </div>
          </ScrollArea>
        </SheetContent>
      </Sheet>
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