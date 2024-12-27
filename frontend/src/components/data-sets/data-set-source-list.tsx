import { ApiClient } from "@/lib/api.ts";
import { useCallback, useEffect, useState } from "react";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { SourcePlugin, CatalogSource } from "@/lib/types.ts";
import { useNavigate } from "react-router-dom";
import { Separator } from "@/components/ui/separator.tsx";
import { DataSetCategorySourceList } from "@/components/data-sets/data-set-source-category-list";

const api = new ApiClient(authenticationProviderInstance);

export interface DataSetProductSourceListProps {
  dataSetId: number;
}

export function DataSetProductSourceList({dataSetId}: DataSetProductSourceListProps) {
  const [productSources, setProductSources] = useState<CatalogSource[]>([]);
  const [documentSources, setDocumentSources] = useState<CatalogSource[]>([]);
  const [productSourcePlugins, setProductSourcePlugins] = useState<SourcePlugin[]>([]);
  const [documentSourcePlugins, setDocumentSourcePlugins] = useState<SourcePlugin[]>([]);
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

  const handleAddProductSource = async (source: SourcePlugin) => {
    await api.dataSets().addDataSetProductSource(dataSetId, source.plugin_name);
    await loadProductSources();
  }

  const handleConfigProductSource = async (productSource: CatalogSource) => {
    console.log("In a new config handler")
    navigate(`/data-sets/${dataSetId}/product-sources/${productSource.id}`);
  }

  const handleSyncProductSource = async (productSource: CatalogSource) => {
    await api.dataSets().syncDataSetProductSource(dataSetId, productSource.id);
  }

  const handleRemoveProductSource = async (productSource: CatalogSource) => {
    await api.dataSets().removeDataSetProductSource(dataSetId, productSource.id);
    await loadProductSources();
  }

  const loadDocumentSources = useCallback(async () => {
    const sources = await api.dataSets().getDataSetDocumentSources(dataSetId);
    setDocumentSources(sources);
    const systemPlugins = await api.getAllDocumentSourcePlugins();
    setDocumentSourcePlugins(systemPlugins);
  }, [dataSetId]);

  useEffect(() => {
    loadDocumentSources();
  }, [loadDocumentSources, dataSetId]);

  const handleAddDocumentSource = async (source: SourcePlugin) => {
    await api.dataSets().addDataSetDocumentSource(dataSetId, source.plugin_name);
    await loadDocumentSources();
  }

  const handleConfigDocumentSource = async (productSource: CatalogSource) => {
    navigate(`/data-sets/${dataSetId}/document-sources/${productSource.id}`);
  }

  const handleSyncDocumentSource = async (documentSource: CatalogSource) => {
    await api.dataSets().syncDataSetDocumentSource(dataSetId, documentSource.id);
  }

  const handleRemoveDocumentSource = async (documentSource: CatalogSource) => {
    await api.dataSets().removeDataSetDocumentSource(dataSetId, documentSource.id);
    await loadDocumentSources();
  }  

  return (
    <>
      <DataSetCategorySourceList
        category="Products"
        sources={productSources}
        plugins={productSourcePlugins}
        handleAdd={handleAddProductSource}
        handleConfig={handleConfigProductSource}
        handleSync={handleSyncProductSource}
        handleRemove={handleRemoveProductSource}
      />
      <Separator className="my-6"/>    
      <DataSetCategorySourceList
        category="Documents"
        sources={documentSources}
        plugins={documentSourcePlugins}
        handleAdd={handleAddDocumentSource}
        handleConfig={handleConfigDocumentSource}
        handleSync={handleSyncDocumentSource}
        handleRemove={handleRemoveDocumentSource}
      />
      
    </>
  );
}
