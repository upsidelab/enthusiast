import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";

export function DataSetList() {
  const {dataSets} = useApplicationContext()!;
  const navigate = useNavigate();

  return (
    <>
      <div className="flex flex-col items-end mb-4">
        <Button variant="default" onClick={() => navigate('/data-sets/new') }>New Data Set</Button>
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
             </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
}
