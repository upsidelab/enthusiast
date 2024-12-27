import { useEffect, useState } from 'react';
import { cn } from "@/lib/utils.ts";
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { MessageFeedbackForm } from "@/components/message-feedback/message-feedback-form.tsx";
import { CopyToClipboardButton } from '@/components/conversation-view/copy-to-clipboard-button.tsx';
import { FeedbackButton } from '@/components/conversation-view/feedback-button.tsx';

export interface MessageBubbleProps {
  text: string;
  variant: "primary" | "secondary";
  questionId: number | null;
}

export function MessageBubble({ text, variant, questionId }: MessageBubbleProps) {
  const [sanitizedHtml, setSanitizedHtml] = useState<string>("");
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  useEffect(() => {
    const processText = async () => {
      const rawHtml = await marked(text);
      const cleanHtml = DOMPurify.sanitize(rawHtml);
      setSanitizedHtml(cleanHtml);
    };

    processText();
  }, [text]);

  const shouldShowActionButtons = variant === 'secondary' && questionId !== null;

  const handleFeedbackClick = () => {
    setIsFeedbackOpen((prev) => !prev);
  };

  return (
    <div className="message-bubble-container flex">
      <div
        className={cn(
          "flex flex-col max-w-[75%] items-centered gap-2 rounded-lg px-3 py-2 text-sm",
          variant === "primary"
            ? "ml-auto bg-primary text-primary-foreground"
            : "bg-muted"
        )}
      >
        <div className={variant} dangerouslySetInnerHTML={{ __html: sanitizedHtml }}/>
        {shouldShowActionButtons &&
          <div className="mt-4 flex items-center">
            <FeedbackButton isOpen={isFeedbackOpen} onClick={handleFeedbackClick} />
            <CopyToClipboardButton message={text} variant="ghost" />
          </div>
        }

        {isFeedbackOpen &&
          <div className="feedback-form-modal mx-4">
            <MessageFeedbackForm messageId={questionId} />
          </div>
        }
      </div>
    </div>
  );
}
