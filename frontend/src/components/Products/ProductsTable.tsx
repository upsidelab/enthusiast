import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { useEffect, useState } from "react";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { ApiClient, Product } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
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

export function ProductsTable() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const itemsPerPage = 25;
  const { dataSetId } = useApplicationContext()!;

  useEffect(() => {
    if (dataSetId === null) {
      return;
    }

    const loadData = async () => {
      const response = await api.getProducts(dataSetId, currentPage);
      setProducts(response.results);
      setTotalProducts(response.count);
      setIsLoading(false);
    };

    loadData();
  }, [dataSetId, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const totalPages = Math.ceil(totalProducts / itemsPerPage);

  if (products.length === 0 && !isLoading) {
    return (
      <div className="text-center">
        <h2 className="font-bold">No products available</h2>
      </div>
    );
  }

  return (
    <SkeletonLoader skeleton={<Skeleton className="w-full h-[100px]" />} isLoading={isLoading}>
      <Table>
        <TableCaption>Sync Status: Manual</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Slug</TableHead>
            <TableHead>SKU</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Categories</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.map((product, index) => (
            <TableRow key={index}>
              <TableCell>{product.slug}</TableCell>
              <TableCell>{product.sku}</TableCell>
              <TableCell>{product.name}</TableCell>
              <TableCell>{product.description}</TableCell>
              <TableCell>{product.categories}</TableCell>
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