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

export type Document = {
  id: number;
  url: string;
  title: string;
  content: string;
}

export type Conversation = {
  started_at: Date;
  model: string;
  dimensions: number;
  data_set: string;
}

export type Token = {
  token: string;
}

export type Answer = {
  conversation_id: number;
  query_message: string;
  answer: string;
}

export type Account = {
  email: string;
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

  async getDocuments(dataSetId: number): Promise<Document[]> {
    const response = await fetch(`${this.apiBase}/api/documents/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Document[]>;
  }

  async getConversations(dataSetId: number): Promise<Conversation[]> {
    const response = await fetch(`${this.apiBase}/api/conversations/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Conversation[]>;
  }

  async getAnswer(conversation_id: number | null, message: string): Promise<Answer> {
    type RequestBody = {
       question_message: string;
       conversation_id?: number;
     };

    const body: RequestBody = { "question_message": message }
    if (conversation_id !== null) {
      body.conversation_id = conversation_id
    }

    const response = await fetch(`${this.apiBase}/api/ask/`, {
      headers: {
        ...this._requestConfiguration().headers,
        'Content-Type': 'application/json'
      },
      method: 'POST',
      body: JSON.stringify(body)
    });

    return await response.json() as Promise<Answer>;
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

  async getAccount(): Promise<Account> {
    const response = await fetch(`${this.apiBase}/api/account`, this._requestConfiguration());
    return await response.json() as Promise<Account>;
  }

  _requestConfiguration(): RequestInit {
    return {
      headers: {
        'Authorization': `Token ${this.authenticationProvider.token}`
      }
    }
  }
}
