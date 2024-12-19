import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ApiClient } from "@/lib/api.ts";
import { useCallback, useEffect, useState } from "react";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { AddProductSourcePluginSelector } from "@/components/data-sets/add-product-source-plugin-selector.tsx";
import { Separator } from "@/components/ui/separator.tsx";
import { ProductSourcePlugin, ProductSource } from "@/lib/types.ts";
import { useNavigate } from "react-router-dom";

const api = new ApiClient(authenticationProviderInstance);

export interface DataSetProductSourceListProps {
  dataSetId: number;
}

export function DataSetProductSourceList({dataSetId}: DataSetProductSourceListProps) {
  const [productSources, setProductSources] = useState<ProductSource[]>([]);
  const [productSourcePlugins, setProductSourcePlugins] = useState<ProductSourcePlugin[]>([]);
  const navigate = useNavigate();

  const loadProductSources = useCallback(async () => {
    const sources = await api.dataSets().getDataSetProductSources(dataSetId);
    setProductSources(sources);
    const systemPlugins = await api.getAllProductSourcePlugins();
    setProductSourcePlugins(systemPlugins);
  }, [dataSetId]);

  useEffect(() => {
    loadProductSources();
  }, [loadProductSources, dataSetId]);

  const handleAddProductSource = async (source: ProductSourcePlugin) => {
    await api.dataSets().addDataSetProductSource(dataSetId, source.plugin_name);
    await loadProductSources();
  }

  const handleSyncProductSource = async (productSource: ProductSource) => {
    console.log("Enqueue task to sync plugin: ", productSource.id)
  }

  const handleRemoveProductSource = async (productSource: ProductSource) => {
    await api.dataSets().removeDataSetProductSource(dataSetId, productSource.id);
    await loadProductSources();
  }

  return (
    <>
      <AddProductSourcePluginSelector productSourcePlugins={productSourcePlugins} onSubmit={handleAddProductSource}/>
      <Separator className="my-6"/>
      {productSources.length > 0 &&
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Actions</TableHead>
              <TableHead></TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {productSources.length > 0 && productSources.map((productSource, index) => (
              <TableRow key={index}>
                <TableCell width="75%">
                  {productSource.plugin_name}
                </TableCell>
                <TableCell className="flex space-x-4" width="25%">
                  <Button onClick={() => {
                    navigate(`/data-sets/${dataSetId}/product-sources/${productSource.id}`)
                  }} variant="secondary">Configure</Button>
                </TableCell>
                <TableCell>
                  <Button onClick={() => {
                    handleSyncProductSource(productSource)
                  }} variant="secondary">Sync</Button>
                </TableCell>
                <TableCell>
                  <Button onClick={() => {
                    handleRemoveProductSource(productSource)
                  }} variant="secondary">Remove</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      }
    </>
  );
}
