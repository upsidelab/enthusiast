import { cn } from "@/lib/utils.ts";
import styles from './message-bubble-typing.module.css';

export interface MessageBubbleTypingProps {
  statusText: string;
}

export function MessageBubbleTyping({ statusText }: MessageBubbleTypingProps) {
  return (
    <div className="flex flex-col gap-2">
      <div className={cn("items-centered rounded-lg px-3 py-4 text-sm", styles.typing)}>
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
      </div>
      <p className="text-sm ml-2 -mt-1 text-muted-foreground">{statusText}</p>
    </div>
  );
}
