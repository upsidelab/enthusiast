import { AuthenticationProvider } from "./authentication-provider.ts";

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

export type Token = {
  token: string;
}

export class ApiClient {
  private readonly apiBase: string;

  constructor(private readonly authenticationProvider: AuthenticationProvider) {
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

  async login(email: string, password: string): Promise<Token> {
    const response = await fetch(`${this.apiBase}/api/auth/login`, {
      headers: {
        'Content-Type': 'application/json'
      },
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    if (response.status !== 200) {
      throw 'Could not sign in';
    }
    
    return await response.json() as Promise<Token>;
  }

  _requestConfiguration(): RequestInit {
    return {
      headers: {
        'Authorization': `Token ${this.authenticationProvider.token}`
      }
    }
  }
}
