export type DataSet = {
  id: number;
  code: string;
  name: string;
}

export type Product = {
  id: number;
  name: string;
  sku: string;
  slug: string;
  description: string;
  categories: string;
}

export type Content = {
  id: number;
  url: string;
  title: string;
  content: string;
}

export type User = {
  status: string;
}

export class ApiClient {
  private readonly apiBase: string;

  constructor(private readonly authenticationProvider) {
    this.apiBase = import.meta.env.VITE_API_BASE;
  }

  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets`, this._requestConfiguration());
    return await response.json() as Promise<DataSet[]>;
  }

  async getProducts(dataSetId: number): Promise<Product[]> {
    const response = await fetch(`${this.apiBase}/api/products/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Product[]>;
  }

  async getContents(dataSetId: number): Promise<Content[]> {
    const response = await fetch(`${this.apiBase}/api/contents/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Content[]>;
  }

  async getUser(): Promise<User> {
    const response = await fetch(`${this.apiBase}/api/user`, this._requestConfiguration());
    return await response.json() as Promise<User>;
  }

  _requestConfiguration(): RequestInit {
    return {
      headers: {
        'Authorization': `Bearer ${this.authenticationProvider.token}`
      }
    }
  }
}
