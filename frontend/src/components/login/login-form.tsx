import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { HTMLAttributes, SyntheticEvent, useState } from "react";
import { Spinner } from "@/components/util/spinner.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert.tsx";

const api = new ApiClient(authenticationProviderInstance);

interface LoginFormProps extends HTMLAttributes<HTMLDivElement> {
  onSuccess: (api: ApiClient) => Promise<void>;
}

export function LoginForm({ className, onSuccess, ...props }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  const onSubmit = async (event: SyntheticEvent) => {
    event.preventDefault();
    setIsLoading(true);

    const form = event.target as HTMLFormElement;
    const email = (form.email as HTMLInputElement).value;
    const password = (form.password as HTMLInputElement).value;

    try {
      await api.login(email, password);
      await onSuccess(api);
    } catch {
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <form onSubmit={onSubmit}>
        <div className="grid gap-2">
          <div className="grid gap-1">
            {isError && <Alert variant="destructive">
              <AlertTitle>Invalid email or password</AlertTitle>
              <AlertDescription>Make sure that the credentials that you've provided are correct and try again.</AlertDescription>
            </Alert>}
            <Input
              id="email"
              name="email"
              placeholder="user@example.com"
              type="email"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isLoading}
            />
            <Input
              id="password"
              name="password"
              placeholder="password"
              type="password"
              autoCapitalize="none"
              autoComplete="off"
              autoCorrect="off"
              disabled={isLoading}
            />
          </div>
          <Button type="submit" disabled={isLoading}>
            {isLoading && <Spinner />}
            Continue
          </Button>
        </div>
      </form>
    </div>
  );
}