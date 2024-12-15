import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { PaginatedTable } from "@/components/util/PaginatedTable.tsx";
import { Product } from "@/lib/types.ts";

const api = new ApiClient(authenticationProviderInstance);

export function ProductsTable() {
  const { dataSetId } = useApplicationContext()!;

  const loadProducts = async (page: number) => {
    if (dataSetId === null) {
      return;
    }

    return await api.catalog().getProducts(dataSetId, page);
  };

  return (
    <PaginatedTable<Product>
      loadItems={loadProducts}
      itemsReloadDependencies={dataSetId}
      noItemsMessage="No products avialable"
      tableFooter="Sync Status: Manual"
      tableHeaders={["Slug", "SKU", "Name", "Description", "Categories"]}
      tableRow={(product, index) => {
        return (
          <TableRow key={index}>
            <TableCell>{product.slug}</TableCell>
            <TableCell>{product.sku}</TableCell>
            <TableCell>{product.name}</TableCell>
            <TableCell>{product.description}</TableCell>
            <TableCell>{product.categories}</TableCell>
          </TableRow>
        )
      }}
    />
  );
}
