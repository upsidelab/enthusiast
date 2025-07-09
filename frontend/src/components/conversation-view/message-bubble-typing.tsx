import styles from './message-bubble-typing.module.css';
import { cn } from "@/lib/utils.ts";

export interface MessageBubbleTypingProps {
  text: string | null;
}

export function MessageBubbleTyping({ text }: MessageBubbleTypingProps) {
  return (
    <div className="flex flex-col">
      <div className={cn("items-centered rounded-lg px-3 py-4 text-sm", styles.typing)}>
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
      </div>
      <p className="text-sm ml-2 -mt-1">{text}</p>
    </div>
  );
}
