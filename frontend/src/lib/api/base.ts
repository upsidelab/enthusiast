import { AuthenticationProvider } from "@/lib/authentication-provider.ts";

export abstract class BaseApiClient {
  constructor(protected readonly apiBase: string, protected readonly authenticationProvider: AuthenticationProvider) {}

  _requestConfiguration(): RequestInit {
    return {
      headers: {
        'Authorization': `Token ${this.authenticationProvider.token}`,
        "Content-Type": "application/json"
      }
    }
  }
}
