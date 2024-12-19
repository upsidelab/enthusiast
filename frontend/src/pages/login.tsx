import { LoginForm } from "@/components/login/login-form.tsx";
import logoUrl from '@/assets/logo.png';

export function LoginPage() {
  return (
    <>
      <div className="container relative hidden h-full flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0">
        <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
          <div className="absolute inset-0 bg-zinc-900" />
          <div className="relative z-20 flex items-center text-lg font-medium">
            <img src={logoUrl} alt="Upside" className="w-10 h-10" />
          </div>
          <div className="relative z-20 mt-auto">
            <blockquote className="space-y-2">
              <p className="text-lg">
                &ldquo;This application is an essential tool for any eCommerce business looking to streamline processes, enhance customer experiences, and ultimately boost sales. I can't recommend it enough!&rdquo;
              </p>
              <footer className="text-sm">John Appleseed, COO at ACME</footer>
            </blockquote>
          </div>
        </div>
        <div className="lg:p-8">
          <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
            <div className="flex flex-col space-y-2 text-center">
              <h1 className="text-2xl font-semibold tracking-tight">
                Login to continue
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
