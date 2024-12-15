import { AuthenticationProvider } from "@/lib/authentication-provider.ts";
import { Document, PaginatedResult, Product } from "@/lib/api.ts";

export class CatalogApiClient {
  constructor(private readonly apiBase: string, private readonly authenticationProvider: AuthenticationProvider) {}

  async getProducts(dataSetId: number, page: number = 1): Promise<PaginatedResult<Product>> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/products?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Product>>;
  }

  async getDocuments(dataSetId: number, page: number = 1): Promise<PaginatedResult<Document>> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/documents?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Document>>;
  }

  _requestConfiguration(): RequestInit {
    return {
      headers: {
        'Authorization': `Token ${this.authenticationProvider.token}`,
        "Content-Type": "application/json"
      }
    }
  }
}
