import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import { DataSet } from "@/lib/types.ts";

const api = new ApiClient(authenticationProviderInstance);

export function DataSetList() {
  const {dataSets} = useApplicationContext()!;
  const navigate = useNavigate();

  const handleSyncAllProductSources = async () => {
    await api.dataSets().syncAllProductSources();
  }

  const handleSyncDataSetProductSources = async (dataSet: DataSet) => {
    await api.dataSets().syncDataSetProductSources(dataSet.id);
  }

  return (
    <>
      <div className="flex flex-row justify-end items-center space-x-4 mb-4">
        <Button variant="default" onClick={() => navigate('/data-sets/new') }>New Data Set</Button>
        <Button variant="default" onClick={() => handleSyncAllProductSources() }>Sync All</Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {dataSets.map((item, index) => (
            <TableRow key={index}>
              <TableCell width="75%">
                {item.name}
              </TableCell>
              <TableCell className="flex space-x-4" width="25%">
                <Button onClick={() => {
                  navigate(`/data-sets/${item.id}/users`)
                }} variant="secondary">Manage Access</Button>
              </TableCell>
              <TableCell>
                <Button onClick={() => {
                  navigate(`/data-sets/${item.id}/product-sources`)
                }} variant="secondary">Product Sources</Button>
              </TableCell>
              <TableCell>
                <Button onClick={() => {
                  handleSyncDataSetProductSources(item)
                }} variant="secondary">Sync</Button>
              </TableCell>
             </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
}
