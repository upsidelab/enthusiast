import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { PaginatedTable } from "@/components/util/paginated-table.tsx";
import { Product } from "@/lib/types.ts";
import { IndexingStatusIcon } from "@/components/util/indexing-status-icon.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function ProductsList() {
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
      tableHeaders={["", "Slug", "SKU", "Name", "Description", "Categories", "Properties"]}
      tableRow={(product, index) => {
        return (
          <TableRow key={index}>
            <TableCell width="1%">
              <IndexingStatusIcon isIndexed={true} />
            </TableCell>
            <TableCell>{product.slug}</TableCell>
            <TableCell>{product.sku}</TableCell>
            <TableCell>{product.name}</TableCell>
            <TableCell>{product.description}</TableCell>
            <TableCell>{product.categories}</TableCell>
            <TableCell>{product.properties}</TableCell>
          </TableRow>
        )
      }}
    />
  );
}
