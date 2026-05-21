import { AuthenticationProvider, getCsrfToken } from "@/lib/authentication-provider.ts";

export abstract class BaseApiClient {
  constructor(protected readonly apiBase: string, protected readonly authenticationProvider: AuthenticationProvider) {}

  _requestConfiguration(): RequestInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (this.authenticationProvider.isAuthenticated()) {
      const csrf = getCsrfToken();
      if (csrf) headers["X-CSRFToken"] = csrf;
    }
    return {
      credentials: "include",
      headers,
    };
  }
}
