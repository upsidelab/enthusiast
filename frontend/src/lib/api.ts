import { AuthenticationProvider, getCsrfToken } from "./authentication-provider.ts";
import { UsersApiClient } from "@/lib/api/users.ts";
import { CatalogApiClient } from "@/lib/api/catalog.ts";
import { DataSetsApiClient } from "@/lib/api/data-sets.ts";
import { ConversationsApiClient } from "@/lib/api/conversations.ts";
import { ServiceAccountsApiClient } from "@/lib/api/service-accounts.ts";
import { Account, SourcePlugin, User } from "@/lib/types.ts";
import { ConfigApiClient } from "@/lib/api/config.ts";
import {AgentsApiClient} from "@/lib/api/agents.ts";

export type Token = { token: string };

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
  streaming: boolean;
}

export class ApiClient {
  private readonly apiBase: string;

  constructor(private readonly authenticationProvider: AuthenticationProvider) {
    this.apiBase = import.meta.env.VITE_API_BASE;
  }

  async login(email: string, password: string): Promise<void> {
    const csrfRes = await fetch(`${this.apiBase}/api/auth/csrf`, { credentials: "include" });
    const { csrfToken } = (await csrfRes.json()) as { csrfToken: string };
    const response = await fetch(`${this.apiBase}/api/auth/login`, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (response.status !== 200) throw new Error("Could not sign in");
  }

  async logout(): Promise<void> {
    const csrf = await fetch(`${this.apiBase}/api/auth/csrf`, { credentials: "include" }).then((r) => r.json()) as { csrfToken: string };
    await fetch(`${this.apiBase}/api/auth/logout`, {
      credentials: "include",
      headers: { "X-CSRFToken": csrf.csrfToken },
      method: "POST",
    });
    this.authenticationProvider.logout();
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
    return (await response.json()).choices as SourcePlugin[];
  }

  async getAllDocumentSourcePlugins(): Promise<SourcePlugin[]> {
    const response = await fetch(`${this.apiBase}/api/plugins/document_source_plugins?page_size=1000`, this._requestConfiguration());
    return (await response.json()).choices as SourcePlugin[];
  }

  async getAllEcommerceIntegrationPlugins(): Promise<SourcePlugin[]> {
    const response = await fetch(`${this.apiBase}/api/plugins/ecommerce_integration_plugins?page_size=1000`, this._requestConfiguration());
    return (await response.json()).choices as SourcePlugin[];
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

  config(): ConfigApiClient {
    return new ConfigApiClient(this.apiBase, this.authenticationProvider);
  }

  agents(): AgentsApiClient {
    return new AgentsApiClient(this.apiBase, this.authenticationProvider);
  }

  _requestConfiguration(): RequestInit {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (this.authenticationProvider.isAuthenticated()) {
      const csrf = getCsrfToken();
      if (csrf) headers["X-CSRFToken"] = csrf;
    }
    return { credentials: "include", headers };
  }
}
