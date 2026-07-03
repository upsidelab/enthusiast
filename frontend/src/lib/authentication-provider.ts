export interface AuthenticationProvider {
  isAuthenticated(): boolean;
  login(): void;
  logout(): void;
}

const sessionAuthKey = "auth_session";

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(?:^|; )" + name.replace(/([.*+?^${}()|[\]\\])/g, "\\$1") + "=([^;]*)"));
  return match ? decodeURIComponent(match[1]) : null;
}

export function getCsrfToken(): string | null {
  return getCookie("csrftoken");
}

class EnthusiastAuthenticationProvider implements AuthenticationProvider {
  constructor() {}

  isAuthenticated(): boolean {
    return sessionStorage.getItem(sessionAuthKey) !== null;
  }

  login(): void {
    sessionStorage.setItem(sessionAuthKey, "true");
  }

  logout(): void {
    sessionStorage.removeItem(sessionAuthKey);
  }
}

export const authenticationProviderInstance: AuthenticationProvider = new EnthusiastAuthenticationProvider();
