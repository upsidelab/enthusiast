import { Button } from "@/components/ui/button.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const api = new ApiClient(authenticationProviderInstance);

export function NoDataSets() {
  const handleLogout = async () => {
    await api.logout();
    window.location.href = "/login";
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen space-y-6 bg-gray-50 p-6">
      <h1 className="text-2xl font-bold">You currently don't have access to any data sets.</h1>
      <p className="text-center">Please contact your administrator to request access.</p>
      <Button onClick={handleLogout} className="mt-4">Sign Out</Button>
    </div>
  );
}
