import { ReactNode, useEffect, useState } from "react";
import { PaginatedResult } from "@/lib/types.ts";
import { SkeletonLoader } from "@/components/util/skeleton-loader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { Table, TableBody, TableCaption, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious
} from "@/components/ui/pagination.tsx";
import RenderPaginationItems from "@/components/util/pagination-utils.tsx";

interface PaginatedTableProps<T> {
  loadItems: (page: number) => Promise<PaginatedResult<T> | undefined>;
  itemsReloadDependencies?: unknown;
  noItemsMessage: string;
  tableFooter?: string;
  tableHeaders: string[];
  tableRow: (item: T, index: number) => ReactNode;
}

export function PaginatedTable<T>({
                                    loadItems,
                                    itemsReloadDependencies,
                                    noItemsMessage,
                                    tableHeaders,
                                    tableRow,
                                    tableFooter
                                  }: PaginatedTableProps<T>) {
  const [items, setItems] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 25;

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const loadedItems = await loadItems(currentPage);
        if (loadedItems) {
          setItems(loadedItems.results);
          setTotalItems(loadedItems.count);
        } else {
          setItems([]);
          setTotalItems(0);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [currentPage, loadItems, itemsReloadDependencies]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  if (items.length === 0 && !isLoading) {
    return (
      <div className="text-center">
        <h2 className="font-bold">{noItemsMessage}</h2>
      </div>
    );
  }

  return (
    <SkeletonLoader skeleton={<Skeleton className="w-full h-[100px]"/>} isLoading={isLoading}>
      <Table>
        {tableFooter && <TableCaption>{tableFooter}</TableCaption>}
        <TableHeader>
          <TableRow>
            {tableHeaders.map((header) => <TableHead>{header}</TableHead>)}
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item, index) => tableRow(item, index))}
        </TableBody>
      </Table>
      {totalPages > 1 &&
        <Pagination className="my-8 text-lg">
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
        }
    </SkeletonLoader>
  )
}
