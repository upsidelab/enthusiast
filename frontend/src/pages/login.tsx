import { useEffect } from "react";
import { LoginForm } from "@/components/login/login-form.tsx";
import logoUrl from "@/assets/logo.png";
import logoSvgUrl from "@/assets/logo.svg";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";
import { useNavigate } from "react-router-dom";
import { SSOLoginForm } from "@/components/login/sso-login-form.tsx";

const api = new ApiClient(authenticationProviderInstance);

async function continueAfterLogin(navigate: (path: string) => void) {
  authenticationProviderInstance.login();
  const dataSets = await api.dataSets().getDataSets();
  if (dataSets.length === 0) {
    const account = await api.getAccount();
    if (account.isStaff) {
      navigate("/onboarding");
    } else {
      navigate("/no-data-sets");
    }
  } else {
    const dataSetAgents = await api.agents().getDatasetAvailableAgents(dataSets[0].id!);
    const agentId = dataSetAgents?.[0]?.id;
    const page = agentId
      ? `/data-sets/${dataSets[0].id}/chat/new/${agentId}`
      : `/data-sets/${dataSets[0].id}/chat/new`;
    navigate(page);
  }
}

export function LoginPage() {
  const navigate = useNavigate();

  useEffect(() => {
    api
      .getAccount()
      .then(() => continueAfterLogin(navigate))
      .catch(() => {});
  }, [navigate]);

  const onSuccess = async () => {
    await continueAfterLogin(navigate);
  };

  return (
    <>
      <div className="container relative hidden h-full flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0">
        <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
          <div className="absolute inset-0 bg-zinc-900" />
          <div className="relative z-20 flex items-center text-lg font-medium">
            <img src={logoUrl} srcSet={logoSvgUrl} alt="Enthusiast" className="w-10 h-10" />
            <p className="ml-4 text-2xl">
              enthusiast.
            </p>
          </div>
        </div>
        <div className="lg:p-8">
          <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
            <div className="flex flex-col space-y-2 text-center">
              <h1 className="text-2xl font-semibold tracking-tight">
                Log in to continue
              </h1>
              <p className="text-sm text-muted-foreground">
                Enter your email and password to get started
              </p>
            </div>
            <LoginForm onSuccess={onSuccess}/>
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">
                      Or
                    </span>
                  </div>
                </div>
                <SSOLoginForm />
              </>
          </div>
        </div>
      </div>
    </>
  )
}