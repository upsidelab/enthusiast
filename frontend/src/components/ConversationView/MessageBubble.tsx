import { Button } from "@/components/ui/button.tsx";
import { useEffect, useState } from 'react';
import { cn } from "@/lib/utils.ts";
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { MessageFeedbackForm } from "@/components/MessageFeedback/MessageFeedbackForm.tsx";
import { ChevronDownIcon, ChevronUpIcon } from "@radix-ui/react-icons";

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

  const shouldShowFeedbackButton = variant === 'secondary' && questionId !== null;

  const handleFeedbackClick = () => {
    setIsFeedbackOpen((prev) => !prev);
  };

  return (
    <div className="message-bubble-container">
      <div
        className={cn(
          "flex flex-col w-max max-w-[75%] items-centered gap-2 rounded-lg px-3 py-2 text-sm",
          variant === "primary"
            ? "ml-auto bg-primary text-primary-foreground"
            : "bg-muted"
        )}
      >
        <div className={variant} dangerouslySetInnerHTML={{ __html: sanitizedHtml }}/>
        {shouldShowFeedbackButton &&
          <div className="mt-4">
            <Button onClick={handleFeedbackClick} variant="ghost">
              Provide feedback for this response
              <span className="ml-1">
                {isFeedbackOpen ? <ChevronUpIcon/> : <ChevronDownIcon />}
              </span>
            </Button>
          </div>
        }

        {isFeedbackOpen &&
          <div className="feedback-form-modal mx-4">
            <MessageFeedbackForm questionId={questionId} />
          </div>
        }
      </div>
    </div>
  );
}
