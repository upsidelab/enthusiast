import { ApiClient, User } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { PaginatedTable } from "@/components/util/PaginatedTable.tsx";
import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { useState } from "react";
import { NewUserModal } from "@/components/users/new-user-modal.tsx";
import { EditUserModal } from "@/components/users/edit-user-modal.tsx";
import { ChangePasswordModal } from "@/components/users/change-password-modal.tsx";
import { Check } from "lucide-react";

const api = new ApiClient(authenticationProviderInstance);

export function UsersList() {
  const [version, setVersion] = useState(0);
  const loadUsers = async (page: number)=> {
    return await api.users().getUsers(page);
  }

  return (
    <>
      <div className="flex flex-col items-end mb-4">
        <NewUserModal onUserCreated={() => setVersion(version + 1)}/>
      </div>
      <PaginatedTable<User>
        loadItems={loadUsers}
        itemsReloadDependencies={version}
        noItemsMessage="No users"
        tableHeaders={["Email", "Active", "Staff", "Actions"]}
        tableRow={(item, index) => {
          return (
            <TableRow key={index}>
              <TableCell width="70%">{item.email}</TableCell>
              <TableCell width="5%">{item.isActive && <Check size={16} />}</TableCell>
              <TableCell width="5%">{item.isStaff && <Check size={16} />}</TableCell>
              <TableCell className="flex space-x-4" width="20%">
                <EditUserModal user={item} onUserUpdated={() => setVersion(version + 1)} />
                <ChangePasswordModal user={item} onUserUpdated={() => setVersion(version + 1)} />
              </TableCell>
            </TableRow>
          )
        }}
      />
    </>
  )
}
