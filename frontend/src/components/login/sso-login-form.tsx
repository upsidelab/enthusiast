import { Button } from "@/components/ui/button.tsx";
import { useEffect, useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert.tsx";

export function SSOLoginForm() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const error = params.get("error");
    if (error) {
      setErrorMessage(error);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const onClick = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE}/login/sso/`;
  };

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