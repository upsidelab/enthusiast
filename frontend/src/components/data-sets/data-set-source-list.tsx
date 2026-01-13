import { useCallback, useEffect, useState } from "react";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { CatalogSource, SourcePlugin } from "@/lib/types.ts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu.tsx";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog.tsx";
import { Plus, RefreshCw, Settings, Trash2, AlertTriangle } from "lucide-react";
import { AddEditSourceModal } from "./add-edit-source-modal.tsx";
import { ButtonWithTooltip } from "@/components/ui/button-with-tooltip.tsx";


const api = new ApiClient(authenticationProviderInstance);

export interface DataSetSourceListProps {
  dataSetId: number;
}

export interface SourceWithType extends CatalogSource {
  type: 'product' | 'document' | 'ecommerce';
}

export function DataSetSourceList({ dataSetId }: DataSetSourceListProps) {
  const [sources, setSources] = useState<SourceWithType[]>([]);
  const [productSourcePlugins, setProductSourcePlugins] = useState<SourcePlugin[]>([]);
  const [documentSourcePlugins, setDocumentSourcePlugins] = useState<SourcePlugin[]>([]);
  const [ecommerceIntegrationPlugins, setEcommerceIntegrationPlugins] = useState<SourcePlugin[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSource, setEditingSource] = useState<SourceWithType | null>(null);
  const [selectedSourceType, setSelectedSourceType] = useState<'product' | 'document' | 'ecommerce'>('product');
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [sourceToDelete, setSourceToDelete] = useState<SourceWithType | null>(null);

  const loadSources = useCallback(async () => {
    const [integration, productSources, documentSources] = await Promise.all([
      api.dataSets().getDataSetECommerceIntegration(dataSetId),
      api.dataSets().getDataSetProductSources(dataSetId),
      api.dataSets().getDataSetDocumentSources(dataSetId),
    ]);

    const sourcesWithType: SourceWithType[] = [
      ...productSources.map(source => ({ ...source, type: 'product' as const })),
      ...documentSources.map(source => ({ ...source, type: 'document' as const }))
    ];

    if (integration) {
      sourcesWithType.unshift({ ...integration, type: 'ecommerce' as const, corrupted: false });
    }

    setSources(sourcesWithType);
  }, [dataSetId]);

  const loadPlugins = useCallback(async () => {
    const [productPlugins, documentPlugins, ecommercePlugins] = await Promise.all([
      api.getAllProductSourcePlugins(),
      api.getAllDocumentSourcePlugins(),
      api.getAllEcommerceIntegrationPlugins()
    ]);

    setProductSourcePlugins(productPlugins);
    setDocumentSourcePlugins(documentPlugins);
    setEcommerceIntegrationPlugins(ecommercePlugins);
  }, []);

  useEffect(() => {
    loadSources();
    loadPlugins();
  }, [loadSources, loadPlugins]);

  const handleAddSource = (sourceType: 'product' | 'document' | 'ecommerce') => {
    setSelectedSourceType(sourceType);
    setEditingSource(null);
    setIsModalOpen(true);
  };

  const handleEditSource = (source: SourceWithType) => {
    setSelectedSourceType(source.type);
    setEditingSource(source);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingSource(null);
  };

  const handleModalSave = async () => {
    await loadSources();
    handleModalClose();
  };

  const handleSyncSource = async (source: SourceWithType) => {
    if (source.type === 'product') {
      await api.dataSets().syncDataSetProductSource(dataSetId, source.id);
    } else if (source.type === 'document') {
      await api.dataSets().syncDataSetDocumentSource(dataSetId, source.id);
    }
  };

  const handleRemoveSource = (source: SourceWithType) => {
    setSourceToDelete(source);
    setIsDeleteDialogOpen(true);
  };

  const confirmDeleteSource = async () => {
    if (!sourceToDelete) return;

    if (sourceToDelete.type === 'product') {
      await api.dataSets().removeDataSetProductSource(dataSetId, sourceToDelete.id);
    } else if (sourceToDelete.type === 'document') {
      await api.dataSets().removeDataSetDocumentSource(dataSetId, sourceToDelete.id);
    } else if (sourceToDelete.type === 'ecommerce') {
      await api.dataSets().removeDataSetECommerceIntegration(dataSetId);
    }
    await loadSources();
    setIsDeleteDialogOpen(false);
    setSourceToDelete(null);
  };

  const cancelDeleteSource = () => {
    setIsDeleteDialogOpen(false);
    setSourceToDelete(null);
  };

  const getAvailablePlugins = () => {
    if (selectedSourceType === 'product') {
      return productSourcePlugins;
    } else if (selectedSourceType === 'document') {
      return documentSourcePlugins;
    } else if (selectedSourceType === 'ecommerce') {
      return ecommerceIntegrationPlugins;
    }
    return [];
  };

  const hasProductPlugins = productSourcePlugins.length > 0;
  const hasDocumentPlugins = documentSourcePlugins.length > 0;
  const hasEcommercePlugins = ecommerceIntegrationPlugins.length > 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-end items-center">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button disabled={!hasProductPlugins && !hasDocumentPlugins && !hasEcommercePlugins}>
              <Plus className="h-4 w-4"/>
              Add integration
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={() => setTimeout(() => handleAddSource('ecommerce'), 1)}
              disabled={!hasEcommercePlugins}
            >
              E-Commerce system
              {!hasEcommercePlugins && (
                <span className="text-xs text-gray-500 ml-2">(No plugins available)</span>
              )}
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => setTimeout(() => handleAddSource('product'), 1)}
              disabled={!hasProductPlugins}
            >
              Product source
              {!hasProductPlugins && (
                <span className="text-xs text-gray-500 ml-2">(No plugins available)</span>
              )}
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => setTimeout(() => handleAddSource('document'), 1)}
              disabled={!hasDocumentPlugins}
            >
              Document source
              {!hasDocumentPlugins && (
                <span className="text-xs text-gray-500 ml-2">(No plugins available)</span>
              )}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {sources.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sources.map((source) => (
              <TableRow key={`${source.type}-${source.id}`}>
                <TableCell className="font-medium">
                  <div className="flex items-center space-x-2">
                    {source.corrupted && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                    <span className={source.corrupted ? "text-muted-foreground" : ""}>
                      {source.plugin_name}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    source.corrupted 
                      ? 'bg-gray-100 text-gray-500'
                      : source.type === 'product'
                        ? 'bg-blue-100 text-blue-800'
                        : source.type === 'document'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-purple-100 text-purple-800'
                  }`}>
                    {source.type === 'product' ? 'Product' : source.type === 'document' ? 'Document' : 'E-Commerce'}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end space-x-2">
                    <ButtonWithTooltip
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditSource(source)}
                      tooltip="Settings"
                    >
                      <Settings className="h-4 w-4"/>
                    </ButtonWithTooltip>
                    <ButtonWithTooltip
                      variant="outline"
                      size="sm"
                      onClick={() => handleSyncSource(source)}
                      tooltip={source.corrupted ? "Cannot sync corrupted source" : "Synchronize data from source"}
                      disabled={source.corrupted}
                    >
                      <RefreshCw className="h-4 w-4"/>
                    </ButtonWithTooltip>
                    <ButtonWithTooltip
                      variant="outline"
                      size="sm"
                      onClick={() => handleRemoveSource(source)}
                      tooltip="Delete"
                    >
                      <Trash2 className="h-4 w-4"/>
                    </ButtonWithTooltip>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-6">
            <p className="text-lg font-medium">No sources configured</p>
            <p className="text-sm">Add your first source to get started</p>
          </div>
          <Button
            onClick={() => handleAddSource('product')}
            disabled={!hasProductPlugins}
          >
            <Plus className="h-4 w-4"/>
            Add a product source
          </Button>
        </div>
      )}

      {isModalOpen && <AddEditSourceModal
        dataSetId={dataSetId}
        sourceType={selectedSourceType}
        source={editingSource}
        availablePlugins={getAvailablePlugins()}
        onClose={handleModalClose}
        open={isModalOpen}
        onSave={handleModalSave}
      />}

      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Source</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-gray-600">
              Are you sure you want to delete the source "{sourceToDelete?.plugin_name}"?
              This action cannot be undone. The data synchronized from this source will be kept.
            </p>
          </div>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={cancelDeleteSource}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDeleteSource}>
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
