import { useState } from "react";
import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { ServiceAccount } from "@/lib/types.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { EditServiceAccountModal } from "./edit-service-account-modal.tsx";
import { PaginatedTable } from "@/components/util/paginated-table.tsx";
import { Check } from "lucide-react";
import { NewServiceAccountModal } from "@/components/service-accounts/new-service-account-modal.tsx";
import { TokenResetModal } from "@/components/service-accounts/token-reset-modal.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function ServiceAccountsList() {
  const [version, setVersion] = useState(0);

  const loadServiceAccounts = async (page: number) => {
    return await api.serviceAccounts().getServiceAccounts(page);
  }

  return (
    <>
      <div className="flex flex-col items-end mb-4">
        <NewServiceAccountModal onServiceAccountCreated={() => setVersion(version + 1)} />
      </div>
      <PaginatedTable<ServiceAccount>
        loadItems={loadServiceAccounts}
        itemsReloadDependencies={version}
        noItemsMessage="No service accounts"
        tableHeaders={["Name", "Date Created", "Active", "Admin", "Actions"]}
        tableRow={(item, index) => {
          return (
            <TableRow key={index}>
              <TableCell width="60%">{item.email}</TableCell>
              <TableCell width="10%">{new Date(item.dateCreated).toLocaleDateString()}</TableCell>
              <TableCell width="5%">{item.isActive && <Check size={16} />}</TableCell>
              <TableCell width="5%">{item.isStaff && <Check size={16} />}</TableCell>
              <TableCell className="flex space-x-4" width="20%">
                <EditServiceAccountModal serviceAccount={item} onServiceAccountUpdated={() => setVersion(version + 1)} />
                <TokenResetModal serviceAccount={item} />
              </TableCell>
            </TableRow>
          )
        }}
      />
    </>
  );
}
