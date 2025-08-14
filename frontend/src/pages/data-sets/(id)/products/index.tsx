import { ProductsList } from "@/components/products/products-list.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";

export function ProductsIndex() {
  return (
    <PageMain>
      <PageHeading title="Manage Products" description="View products synchronized from external systems." />
      <ProductsList />
    </PageMain>
  )
}
