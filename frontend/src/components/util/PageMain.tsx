import { ReactNode } from "react";

export interface PageMainProps {
  children: ReactNode;
}

export function PageMain({ children }: PageMainProps) {
  return (
    <div className="py-4 px-8">
      {children}
    </div>
  )
}
