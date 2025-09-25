import { useEffect, useState } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { MessageFeedbackForm } from "@/components/message-feedback/message-feedback-form.tsx";
import { CopyToClipboardButton } from '@/components/conversation-view/copy-to-clipboard-button.tsx';
import { FeedbackButton } from '@/components/conversation-view/feedback-button.tsx';
import { MessageFiles } from '@/components/conversation-view/message-files';
import { BaseBubble } from '@/components/conversation-view/base-bubble';
import { MessageFile } from './conversation';

export interface MessageBubbleProps {
  text: string;
  variant: "primary" | "secondary";
  questionId: number | null;
  files?: MessageFile[];
}

export function MessageBubble({ text, variant, questionId, files }: MessageBubbleProps) {
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

  const shouldShowActionButtons = variant === 'secondary' && questionId !== null && text;

  const handleFeedbackClick = () => {
    setIsFeedbackOpen((prev) => !prev);
  };

  if (!text && files && files.length > 0) {
    return null;
  }

  return (
    <BaseBubble variant={variant} hasBackground={true}>
      {text && (
        <div className={variant} dangerouslySetInnerHTML={{ __html: sanitizedHtml }}/>
      )}

      {files && files.length > 0 && (
        <MessageFiles files={files} />
      )}
      
      {shouldShowActionButtons && (
        <div className="mt-4 flex items-center">
          <FeedbackButton isOpen={isFeedbackOpen} onClick={handleFeedbackClick} />
          <CopyToClipboardButton message={text} variant="ghost" />
        </div>
      )}

      {isFeedbackOpen && (
        <div className="feedback-form-modal mx-4">
          <MessageFeedbackForm messageId={questionId} />
        </div>
      )}
    </BaseBubble>
  );
}
