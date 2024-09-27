import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Label } from "@/components/ui/label.tsx";
import { HTMLAttributes, SyntheticEvent, useState } from "react";
import { Spinner } from "@/components/util/Spinner.tsx";
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

    const invitationCode = (event.target as any).invitationCode.value;
    authenticationProviderInstance.login(invitationCode);

    try {
      await api.getUser();
      navigate('/campaign');
    } catch (e) {
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
              <AlertTitle>Invalid invitation code</AlertTitle>
              <AlertDescription>Make sure that the code you've provided is correct and try again.</AlertDescription>
            </Alert>}
            <Label className="sr-only" htmlFor="invitationCode">
              Your invitation code
            </Label>
            <Input
              id="invitationCode"
              placeholder="UP-XXXXX-XXXX-XXXX-XXXXX"
              type="text"
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
