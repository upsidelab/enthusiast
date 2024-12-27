import { BaseApiClient } from "@/lib/api/base.ts";
import { PaginatedResult, ServiceAccount } from "@/lib/types.ts";
import { Token } from "@/lib/api.ts";

export type ServiceAccountResponse = {
  id: number;
  email: string;
  date_joined: string;
  is_active: boolean;
  data_set_ids: number[];
}

export type CreateServiceAccountParams = {
  name: string;
  dataSetIds: number[];
  isActive: boolean;
}

export type UpdateServiceAccountParams = CreateServiceAccountParams;

export type CreateServiceAccountPayload = {
  name: string;
  data_set_ids: number[];
  is_active: boolean;
}

export type UpdateServiceAccountPayload = CreateServiceAccountPayload;

export class ServiceAccountsApiClient extends BaseApiClient {
  async getServiceAccounts(page: number): Promise<PaginatedResult<ServiceAccount>> {
    const response = await fetch(`${this.apiBase}/api/service_accounts?page=${page}`, this._requestConfiguration());
    const result = await response.json() as PaginatedResult<ServiceAccountResponse>;

    return {
      count: result.count,
      results: result.results.map((item) => ({
        id: item.id,
        email: item.email,
        dateCreated: item.date_joined,
        dataSetIds: item.data_set_ids,
        isActive: item.is_active
      }))
    };
  }

  async createServiceAccount(serviceAccount: CreateServiceAccountParams): Promise<Token> {
    const payload: CreateServiceAccountPayload = {
      name: serviceAccount.name,
      data_set_ids: serviceAccount.dataSetIds,
      is_active: serviceAccount.isActive
    };

    const response = await fetch(`${this.apiBase}/api/service_accounts/`, {
      ...this._requestConfiguration(),
      method: 'POST',
      body: JSON.stringify(payload)
    });

    return await response.json() as Token;
  }

  async updateServiceAccount(id: number, serviceAccount: UpdateServiceAccountParams): Promise<Response> {
    const payload: UpdateServiceAccountPayload = {
      name: serviceAccount.name,
      data_set_ids: serviceAccount.dataSetIds,
      is_active: serviceAccount.isActive
    };

    return await fetch(`${this.apiBase}/api/service_accounts/${id}`, {
      ...this._requestConfiguration(),
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
  }

  async checkServiceNameAvailability(name: string): Promise<boolean> {
    const response = await fetch(`${this.apiBase}/api/service_accounts/check_name`, {
      ...this._requestConfiguration(),
      method: 'POST',
      body: JSON.stringify({ name })
    });

    const { is_available } = await response.json();
    return is_available;
  }

  async resetServiceAccountToken(id: number): Promise<Token> {
    const response = await fetch(`${this.apiBase}/api/service_accounts/${id}/reset_token`, {
      ...this._requestConfiguration(),
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error('Failed to revoke service account token');
    }

    return await response.json() as Token;
  }
}
