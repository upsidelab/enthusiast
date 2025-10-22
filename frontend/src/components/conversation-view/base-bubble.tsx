import { cn } from "@/lib/utils.ts";

interface BaseBubbleProps {
  variant: "primary" | "secondary";
  children: React.ReactNode;
  className?: string;
  hasBackground?: boolean;
  inMessageGroup?: boolean;
}

export function BaseBubble({ variant, children, className, hasBackground = false, inMessageGroup }: BaseBubbleProps) {
  return (
    <div className={`message-bubble-container flex ${inMessageGroup ? '!mt-2' : ''}`}>
      <div
        className={cn(
          "flex flex-col max-w-[75%] items-centered gap-2 rounded-lg px-3 py-2 text-sm",
          variant === "primary" ? "ml-auto" : "",
          hasBackground && (
            variant === "primary"
              ? "bg-primary text-primary-foreground"
              : "bg-muted"
          ),
          className
        )}
      >
        {children}
      </div>
    </div>
  );
}
