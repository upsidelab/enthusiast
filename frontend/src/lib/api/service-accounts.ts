import { BaseApiClient } from "@/lib/api/base.ts";
import { ServiceAccount } from "@/lib/types.ts";

export class ServiceAccountsApiClient extends BaseApiClient {
  async getServiceAccounts(): Promise<ServiceAccount[]> {
    const response = await fetch(`${this.apiBase}/api/service_accounts/`, this._requestConfiguration());
    return (await response.json()) as ServiceAccount[];
  }

  async createServiceAccount(name: string, datasets: string[]): Promise<ServiceAccount> {
    const response = await fetch(`${this.apiBase}/api/service_accounts/`, {
      ...this._requestConfiguration(),
      method: 'POST',
      body: JSON.stringify({ name, datasets })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Failed to create service account:', errorText);
      throw new Error('Failed to create service account');
    }

    return await response.json() as ServiceAccount;
  }

  async updateServiceAccount(id: number, data: { name?: string; is_active?: boolean }): Promise<void> {
    const response = await fetch(`${this.apiBase}/api/service_accounts/${id}`, {
      ...this._requestConfiguration(),
      method: 'PATCH',
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error('Failed to update service account');
    }
  }

  async checkServiceNameAvailability(name: string): Promise<boolean> {
    const response = await fetch(`${this.apiBase}/api/service_accounts/check_name`, {
      ...this._requestConfiguration(),
      method: 'POST',
      body: JSON.stringify({ name })
    });

    if (!response.ok) {
      throw new Error('Failed to check service account name availability');
    }

    const { is_available } = await response.json();
    return is_available;
  }

  async revokeServiceAccountToken(id: number): Promise<string> {
    const response = await fetch(`${this.apiBase}/api/service_accounts/${id}/revoke_token`, {
      ...this._requestConfiguration(),
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to revoke service account token');
    }

    const { token } = await response.json();
    return token;
  }
}
