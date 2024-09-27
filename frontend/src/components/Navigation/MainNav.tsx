import { cn } from "@/lib/utils";

export function MainNav({className}: React.HTMLAttributes<HTMLElement>) {
  return (
    <nav
      className={cn("flex items-center space-x-4 lg:space-x-6", className)}
    >
      <a
        href="/"
        className="text-sm font-medium transition-colors hover:text-primary"
      >
        Dashboard
      </a>
      <a
        href="/settings"
        className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
      >
        Settings
      </a>
      <a
        href="/docs"
        className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
      >
        Documentation
      </a>
    </nav>
  )
}
