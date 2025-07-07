import { Separator } from "@/components/ui/separator.tsx";
import { cn } from "@/lib/utils.ts";

export interface PageHeadingProps {
  title: string;
  description: string;
  className?: string;
}

export function PageHeading({ title, description, className }: PageHeadingProps) {
  return (
    <div className={cn(className)}>
      <div>
        <h3 className="text-lg font-medium">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <Separator className="my-6"/>
    </div>
  )
}
