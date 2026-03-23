import { ReactNode, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
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

export const DEFAULT_PAGE_PARAM = "page";

interface PaginatedTableProps<T> {
  loadItems: (page: number) => Promise<PaginatedResult<T> | undefined>;
  itemsReloadDependencies?: unknown;
  noItemsMessage: string;
  tableFooter?: string;
  tableHeaders: string[];
  tableHeaderWidths?: string[];
  tableRow: (item: T, index: number) => ReactNode;
  pageParamName?: string;
}

export function PaginatedTable<T>({
                                    loadItems,
                                    itemsReloadDependencies,
                                    noItemsMessage,
                                    tableHeaders,
                                    tableHeaderWidths,
                                    tableRow,
                                    tableFooter,
                                    pageParamName = DEFAULT_PAGE_PARAM,
                                  }: PaginatedTableProps<T>) {
  const [items, setItems] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 25;

  const [searchParams, setSearchParams] = useSearchParams();
  const currentPage = Number(searchParams.get(pageParamName) ?? "1") || 1;

  const handlePageChange = (page: number) => {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev);
      if (page > 1) next.set(pageParamName, page.toString());
      else next.delete(pageParamName);
      return next;
    });
  };

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
        {tableHeaderWidths && (
          <colgroup>
            {tableHeaderWidths.map((w, i) => <col key={i} style={{ width: w }} />)}
          </colgroup>
        )}
        {tableFooter && <TableCaption>{tableFooter}</TableCaption>}
        <TableHeader>
          <TableRow>
            {tableHeaders.map((header, i) => <TableHead key={i}>{header}</TableHead>)}
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
