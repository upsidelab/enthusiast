import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const api = new ApiClient(authenticationProviderInstance);

export async function checkServiceNameAvailability(name: string): Promise<boolean> {
  const response = await api.serviceAccounts().checkServiceNameAvailability(name);
  return response;
}