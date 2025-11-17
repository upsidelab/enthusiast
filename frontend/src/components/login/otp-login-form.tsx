import { Button } from "@/components/ui/button.tsx";
import { useEffect, useState } from "react";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert.tsx";
import { useNavigate } from "react-router-dom";

const api = new ApiClient(authenticationProviderInstance);

interface OtpLoginFormProps {
  onSuccess: (token: string, api: ApiClient) => Promise<void>;
}

export function OtpLoginForm({ onSuccess }: OtpLoginFormProps) {
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const onClick = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE}/api/auth/otp/start`
  }
  useEffect(() => {
      const params = new URLSearchParams(window.location.search);
      const token = params.get("token");
      const error = params.get("error")

      if (token) {
        onSuccess(token, api);
        window.history.replaceState({}, document.title, window.location.pathname);
      }
      if (error) {
      setErrorMessage(error);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [navigate]);
  return (
          <div className="grid gap-1">
            {errorMessage && (
              <Alert variant="destructive">
                <AlertTitle>Login failed</AlertTitle>
                <AlertDescription>{errorMessage}</AlertDescription>
              </Alert>
            )}
            <Button
              variant="outline"
              onClick={onClick}
            >
              Log in with SSO
            </Button>
          </div>
  );
}
