import { AuthenticationProvider } from "./authentication-provider.ts";
import { UsersApiClient } from "@/lib/api/users.ts";
import { CatalogApiClient } from "@/lib/api/catalog.ts";
import { DataSetsApiClient } from "@/lib/api/data-sets.ts";
import { ConversationsApiClient } from "@/lib/api/conversations.ts";
import { ServiceAccountsApiClient } from "@/lib/api/service-accounts.ts";
import { Account, SourcePlugin, User } from "@/lib/types.ts";

export type Token = {
  token: string;
}

type AccountResponse = {
  email: string;
  is_staff: boolean;
}

export type FeedbackData = {
  rating: number | null;
  feedback: string;
}

export type TaskHandle = {
  task_id: string;
}

export class ApiClient {
  private readonly apiBase: string;

  constructor(private readonly authenticationProvider: AuthenticationProvider) {
    this.apiBase = import.meta.env.VITE_API_BASE;
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
    const responseJson = await response.json() as AccountResponse;
    return {
      email: responseJson.email,
      isStaff: responseJson.is_staff
    };
  }

  users(): UsersApiClient {
    return new UsersApiClient(this.apiBase, this.authenticationProvider);
  }

  async getAllUsers(): Promise<User[]> {
    const response = await fetch(`${this.apiBase}/api/users?page_size=1000`, this._requestConfiguration());
    return (await response.json()).results as User[];
  }

  async getAllProductSourcePlugins(): Promise<SourcePlugin[]> {
    const response = await fetch(`${this.apiBase}/api/plugins/product_source_plugins?page_size=1000`, this._requestConfiguration());
    return (await response.json()).results as SourcePlugin[];
  }

  async getAllDocumentSourcePlugins(): Promise<SourcePlugin[]> {
    const response = await fetch(`${this.apiBase}/api/plugins/document_source_plugins?page_size=1000`, this._requestConfiguration());
    return (await response.json()).results as SourcePlugin[];
  }  

  catalog(): CatalogApiClient {
    return new CatalogApiClient(this.apiBase, this.authenticationProvider);
  }

  serviceAccounts(): ServiceAccountsApiClient {
    return new ServiceAccountsApiClient(this.apiBase, this.authenticationProvider);
  }

  dataSets(): DataSetsApiClient {
    return new DataSetsApiClient(this.apiBase, this.authenticationProvider);
  }

  conversations(): ConversationsApiClient {
    return new ConversationsApiClient(this.apiBase, this.authenticationProvider);
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