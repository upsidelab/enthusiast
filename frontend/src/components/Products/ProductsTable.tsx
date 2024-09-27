import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { ApiClient, Product } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function ProductsTable() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      const apiProducts = await api.getProducts(1);
      setProducts(apiProducts);
      setIsLoading(false);
    };

    loadData();
  }, []);

  return (
    <SkeletonLoader skeleton={<Skeleton className="w-full h-[100px]"/>} isLoading={isLoading}>
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
    </SkeletonLoader>
  );
}
