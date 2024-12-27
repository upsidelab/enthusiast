import { ServiceAccount } from "@/lib/types.ts";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Button } from "@/components/ui/button.tsx";
import { TokenGeneratedModal } from "@/components/service-accounts/token-generated-modal.tsx";
import { useState } from "react";

const api = new ApiClient(authenticationProviderInstance);

export interface TokenResetModalProps {
  serviceAccount: ServiceAccount;
}

export function TokenResetModal({serviceAccount}: TokenResetModalProps) {
  const [newToken, setNewToken] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleTokenReset = async () => {
    const { token } = await api.serviceAccounts().resetServiceAccountToken(serviceAccount.id);
    setNewToken(token);
    setIsDialogOpen(true);
  };

  return (
    <>
      <TokenGeneratedModal
        title="Token Reset"
        description="To access the API using this account, use the token provided below. You will only see this token once, so please store it in a safe place."
        token={newToken}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
      />
      <Button variant="secondary" onClick={handleTokenReset}>
        Reset Token
      </Button>
    </>
  );
}
