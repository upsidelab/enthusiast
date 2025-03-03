import styles from './message-bubble-typing.module.css';
import { cn } from "@/lib/utils.ts";

export function MessageBubbleTyping() {
  return (
    <div className="flex">
      <div className={cn("items-centered rounded-lg bg-muted px-3 py-4 text-sm", styles.typing)}>
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
        <div className={styles.typingDot} />
      </div>
    </div>
  );
}
