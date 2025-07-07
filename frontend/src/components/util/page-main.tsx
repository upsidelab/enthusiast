import { ReactNode } from "react";
import { cn } from "@/lib/utils.ts";

export interface PageMainProps {
  className?: string;
  children: ReactNode;
}

export function PageMain({ children, className }: PageMainProps) {
  return (
    <div className={cn("py-4 px-8", className)}>
      {children}
    </div>
  )
}
