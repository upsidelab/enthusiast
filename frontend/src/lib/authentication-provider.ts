export interface AuthenticationProvider {
  token: string | null;
  isAuthenticated(): boolean;
  login(token: string): boolean;
  logout(): void;
}

const tokenKey = 'token';

class DummyAuthenticationProvider implements AuthenticationProvider {
  token: string | null;

  constructor() {
    this.token = localStorage.getItem(tokenKey);
  }

  isAuthenticated(): boolean {
    return this.token !== null;
  }

  login(token: string): boolean {
    this.token = token;
    localStorage.setItem(tokenKey, token);
    return true;
  }

  logout(): void {
    localStorage.removeItem(tokenKey);
    this.token = null;
  }
}

export const authenticationProviderInstance: AuthenticationProvider = new DummyAuthenticationProvider();
