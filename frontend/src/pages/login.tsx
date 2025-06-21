import { LoginForm } from "@/components/login/login-form.tsx";
import logoUrl from '@/assets/logo.png';
import logoSvgUrl from '@/assets/logo.svg';

export function LoginPage() {
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
            <LoginForm />
          </div>
        </div>
      </div>
    </>
  )
}
