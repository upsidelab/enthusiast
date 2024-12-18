import { useState, useEffect } from "react";
import { Table, TableBody, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { ApiClient } from "@/lib/api.ts";
import { ServiceAccount } from "@/lib/types.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Separator } from "@/components/ui/separator.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useNavigate } from "react-router-dom";
import { ServiceAccountRow } from "./ServiceAccountRow.tsx";
import { EditServiceAccountDialog } from "./EditServiceAccountDialog.tsx";
import { RevokeTokenDialog } from "./RevokeTokenDialog.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function ApiConnectionTable() {
  const [serviceAccounts, setServiceAccounts] = useState<ServiceAccount[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isTokenDialogOpen, setIsTokenDialogOpen] = useState(false);
  const [selectedServiceAccount, setSelectedServiceAccount] = useState<ServiceAccount | null>(null);
  const [generatedToken, setGeneratedToken] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [fetchErrorMessage, setFetchErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.serviceAccounts().getServiceAccounts();
        setServiceAccounts(response as ServiceAccount[]);
      } catch (error) {
        console.error("Error fetching data:", error);
        setFetchErrorMessage("Failed to fetch service accounts. Please try again.");
      }
    };

    fetchData();
  }, []);

  const handleEditClick = (serviceAccount: ServiceAccount) => {
    setSelectedServiceAccount(serviceAccount);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedServiceAccount(null);
    setErrorMessage(null);
  };

  const handleFormSubmit = async (values: { name: string }) => {
    if (selectedServiceAccount) {
      try {
        await api.serviceAccounts().updateServiceAccount(selectedServiceAccount.id, { name: values.name });
        const updatedServiceAccounts = await api.serviceAccounts().getServiceAccounts();
        setServiceAccounts(updatedServiceAccounts);
        handleDialogClose();
      } catch (error) {
        console.error("Error updating service account:", error);
        setErrorMessage("Failed to update service account. Please try again.");
      }
    }
  };

  const handleDeactivateServiceAccount = async (serviceAccount: ServiceAccount) => {
    try {
      await api.serviceAccounts().updateServiceAccount(serviceAccount.id, { is_active: false });
      setServiceAccounts((prevServiceAccounts) =>
        prevServiceAccounts.filter((account) => account.id !== serviceAccount.id)
      );
    } catch {
      setErrorMessage("Failed to deactivate service account. Please try again.");
    }
  };

  const handleRevokeToken = async (serviceAccount: ServiceAccount) => {
    try {
      const newToken = await api.serviceAccounts().revokeServiceAccountToken(serviceAccount.id);
      setGeneratedToken(newToken);
      setIsTokenDialogOpen(true);
    } catch (error) {
      console.error("Error revoking token:", error);
      setErrorMessage("Failed to revoke token. Please try again.");
    }
  };

  const handleTokenDialogClose = () => {
    setIsTokenDialogOpen(false);
  };

  const handleCopyToken = () => {
    navigator.clipboard.writeText(generatedToken);
  };

  return (
    <div className="p-4">
      {fetchErrorMessage && <div className="text-red-500 mb-4">{fetchErrorMessage}</div>}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Service Account Name</TableHead>
            <TableHead>Creation Date</TableHead>
            <TableHead>Associated Datasets</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {serviceAccounts.map((serviceAccount, index) => (
            <ServiceAccountRow
              key={index}
              serviceAccount={serviceAccount}
              onEdit={handleEditClick}
              onDeactivate={handleDeactivateServiceAccount}
              onRevokeToken={handleRevokeToken}
            />
          ))}
        </TableBody>
      </Table>
      <Separator className="my-6" />
      <Button variant="default" onClick={() => navigate('/api-connection/new')}>Add New Service Account</Button>

      <EditServiceAccountDialog
        isOpen={isDialogOpen}
        onClose={handleDialogClose}
        onSubmit={handleFormSubmit}
        serviceAccount={selectedServiceAccount}
        errorMessage={errorMessage}
      />

      <RevokeTokenDialog
        isOpen={isTokenDialogOpen}
        onClose={handleTokenDialogClose}
        token={generatedToken}
        onCopy={handleCopyToken}
      />
    </div>
  );
}
