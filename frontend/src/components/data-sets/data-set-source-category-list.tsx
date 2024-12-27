import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import { AddSourcePluginSelector } from "@/components/data-sets/add-source-plugin-selector";
import { SourcePlugin, CatalogSource } from "@/lib/types.ts";

export interface SourceListProps {
  category: string;
  sources: CatalogSource[];
  plugins: SourcePlugin[];
  handleAdd: (plugin: SourcePlugin) => void;
  handleConfig: (source: CatalogSource) => void;
  handleSync: (source: CatalogSource) => void;
  handleRemove: (source: CatalogSource) => void;
}

export function DataSetCategorySourceList({
  category, 
  sources, 
  plugins, 
  handleAdd, 
  handleConfig, 
  handleSync, 
  handleRemove
}: SourceListProps) {
  return (
    <>
      <div className="bg-gray-50 p-4 rounded-md flex items-center space-x-4">
        <div className="text-gray-700 font-semibold">{category}</div>
        <AddSourcePluginSelector sourcePlugins={plugins} onSubmit={handleAdd} />
      </div>
      {sources.length > 0 &&
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
            {sources.length > 0 && sources.map((source, index) => (
              <TableRow key={index}>
                <TableCell width="75%">
                  {source.plugin_name}
                </TableCell>
                <TableCell className="flex space-x-4" width="25%">
                  <Button onClick={() => {
                    handleConfig(source)
                  }} variant="secondary">Configure</Button>
                </TableCell>
                <TableCell>
                  <Button onClick={() => {
                    handleSync(source)
                  }} variant="secondary">Sync</Button>
                </TableCell>
                <TableCell>
                  <Button onClick={() => {
                    handleRemove(source)
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
