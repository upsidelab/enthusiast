import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ApiClient } from "@/lib/api.ts";
import { useCallback, useEffect, useState } from "react";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { AddUserSelector } from "@/components/DataSets/AddUserSelector.tsx";
import { Separator } from "@/components/ui/separator.tsx";
import { User } from "@/lib/types.ts";

const api = new ApiClient(authenticationProviderInstance);

export interface DataSetUserListProps {
  dataSetId: number;
}

export function DataSetUserList({dataSetId}: DataSetUserListProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);

  const loadUsers = useCallback(async () => {
    const users = await api.dataSets().getDataSetUsers(dataSetId);
    setUsers(users);
    const systemUsers = await api.getAllUsers();
    const availableUsers = systemUsers.filter((systemUser) => users.find((user) => user.id === systemUser.id) === undefined);
    setAvailableUsers(availableUsers);
  }, [dataSetId]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers, dataSetId]);

  const handleAddUser = async (user: User) => {
    await api.dataSets().addDataSetUser(dataSetId, user.id);
    await loadUsers();
  }

  const handleRemoveUser = async (user: User) => {
    await api.dataSets().removeDataSetUser(dataSetId, user.id);
    await loadUsers();
  }

  return (
    <>
      <AddUserSelector availableUsers={availableUsers} onSubmit={handleAddUser}/>
      <Separator className="my-6"/>
      {users.length > 0 &&
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.length > 0 && users.map((user, index) => (
              <TableRow key={index}>
                <TableCell width="75%">
                  {user.email}
                </TableCell>
                <TableCell className="flex space-x-4" width="25%">
                  <Button onClick={() => {
                    handleRemoveUser(user)
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
