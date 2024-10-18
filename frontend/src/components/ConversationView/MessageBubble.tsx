import { useEffect, useState } from 'react';
import { cn } from "@/lib/utils.ts";
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export interface MessageBubbleProps {
  text: string;
  variant: "primary" | "secondary";
}

export function MessageBubble({ text, variant }: MessageBubbleProps) {
  const [sanitizedHtml, setSanitizedHtml] = useState<string>("");

  useEffect(() => {
    const processText = async () => {
      const rawHtml = await marked(text);
      const cleanHtml = DOMPurify.sanitize(rawHtml);
      setSanitizedHtml(cleanHtml);
    };

    processText();
  }, [text]);

  return (
    <div
      className={cn(
        "flex w-max max-w-[75%] flex-col gap-2 rounded-lg px-3 py-2 text-sm",
        variant === "primary"
          ? "ml-auto bg-primary text-primary-foreground"
          : "bg-muted"
      )}
    >
      <div className={variant} dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
    </div>
  );
}
