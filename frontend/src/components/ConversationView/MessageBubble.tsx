import { cn } from "@/lib/utils.ts";

export interface MessageBubbleProps {
  text: string;
  variant: "primary" | "secondary"
}

export function MessageBubble({text, variant}: MessageBubbleProps) {
  return (
    <div
      className={cn(
        "flex w-max max-w-[75%] flex-col gap-2 rounded-lg px-3 py-2 text-sm",
        variant === "primary"
          ? "ml-auto bg-primary text-primary-foreground"
          : "bg-muted"
      )}
    >
      {text}
    </div>
  );
}
