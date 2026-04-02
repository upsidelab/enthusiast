import { CheckIcon } from "lucide-react";
import { cn } from "@/lib/utils.ts";
import styles from './message-bubble-typing.module.css';
import type { ToolStep } from "@/lib/types";

export interface MessageBubbleTypingProps {
  steps: ToolStep[];
}

export function MessageBubbleTyping({ steps }: MessageBubbleTypingProps) {
  return (
    <div className="flex flex-col gap-2">
      <div className={cn("items-centered rounded-lg px-3 py-4 text-sm", styles.typing)}>
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
      </div>
      {steps.length === 0 ? (
        <p className="text-sm ml-2 -mt-1 text-muted-foreground">Thinking...</p>
      ) : (
        <div className="ml-2 border-l-2 border-muted-foreground/20 pl-3 space-y-1.5">
          {steps.map((step, i) => (
            <div
              key={i}
              className={cn(
                "flex items-center gap-2 text-sm",
                step.done ? "text-muted-foreground" : "text-foreground font-medium"
              )}
            >
              {step.done ? (
                <CheckIcon className="w-3 h-3 shrink-0" />
              ) : (
                <div className={styles.stepSpinner} />
              )}
              <span>{step.name}{step.input ? <span className="font-normal opacity-60"> — {step.input}</span> : null}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
