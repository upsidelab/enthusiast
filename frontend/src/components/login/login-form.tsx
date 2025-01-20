import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { HTMLAttributes, SyntheticEvent, useState } from "react";
import { Spinner } from "@/components/util/spinner.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useNavigate } from "react-router-dom";
import { ApiClient } from "@/lib/api.ts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function LoginForm({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  async function onSubmit(event: SyntheticEvent) {
    event.preventDefault();
    setIsLoading(true);

    const email = (event.target as HTMLFormElement).email.value;
    const password = (event.target as HTMLFormElement).password.value;

    try {
      const { token } = await api.login(email, password);
      authenticationProviderInstance.login(token);

      const dataSets = await api.dataSets().getDataSets();
      if (dataSets.length === 0) {
        const account = await api.getAccount();
        if (account.isStaff) {
          navigate('/onboarding');
        } else {
          navigate('/no-data-sets');
        }
      } else {
        navigate(`/data-sets/${dataSets[0].id}/chat`);
      }
    } catch {
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  }

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
              placeholder="user@example.com"
              type="email"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isLoading}
            />
            <Input
              id="password"
              placeholder="password"
              type="password"
              autoCapitalize="none"
              autoComplete="off"
              autoCorrect="off"
              disabled={isLoading}
            />
          </div>
          <Button disabled={isLoading}>
            {isLoading && (
              <Spinner />
            )}
            Continue
          </Button>
        </div>
      </form>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t"/>
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or
          </span>
        </div>
      </div>
      <Button disabled={isLoading} variant="outline" asChild>
        <a href="https://upsidelab.io/contact">
          Sign up for a waitlist
        </a>
      </Button>
    </div>
  )
}
