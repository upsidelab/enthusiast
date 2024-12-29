import { Document, PaginatedResult, Product } from "@/lib/types.ts";
import { BaseApiClient } from "@/lib/api/base.ts";

export type DocumentResponse = {
  id: number;
  url: string;
  title: string;
  content: string;
  is_indexed: boolean;
}

export class CatalogApiClient extends BaseApiClient {
  async getProducts(dataSetId: number, page: number = 1): Promise<PaginatedResult<Product>> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/products?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Product>>;
  }

  async getDocuments(dataSetId: number, page: number = 1): Promise<PaginatedResult<Document>> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/documents?page=${page}`, this._requestConfiguration());
    const result = await response.json() as PaginatedResult<DocumentResponse>;

    return {
      count: result.count,
      results: result.results.map((item) => ({
        id: item.id,
        url: item.url,
        title: item.title,
        content: item.content,
        isIndexed: item.is_indexed
      }))
    };
  }
}
