import { useEffect, useState } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { MessageFeedbackForm } from "@/components/message-feedback/message-feedback-form.tsx";
import { CopyToClipboardButton } from '@/components/conversation-view/copy-to-clipboard-button.tsx';
import { FeedbackButton } from '@/components/conversation-view/feedback-button.tsx';
import { BaseBubble } from '@/components/conversation-view/base-bubble';

export interface MessageBubbleProps {
  text: string;
  variant: "primary" | "secondary";
  questionId: number | null;
  inMessageGroup?: boolean;
}

export function MessageBubble({ text, variant, questionId, inMessageGroup }: MessageBubbleProps) {
  const [sanitizedHtml, setSanitizedHtml] = useState<string>("");
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  useEffect(() => {
    const processText = async () => {
      const renderer = new marked.Renderer();
      renderer.link = ({ href, title, tokens }) => {
        const text = tokens.map(token => token.raw).join('');
        const titleAttr = title ? ` title="${title}"` : '';
        return `<a href="${href}" target="_blank" rel="noopener noreferrer"${titleAttr}>${text}</a>`;
      };

      const rawHtml = await marked(text, { renderer });
      const cleanHtml = DOMPurify.sanitize(rawHtml);
      setSanitizedHtml(cleanHtml);
    };

    processText();
  }, [text]);

  const shouldShowActionButtons = variant === 'secondary' && questionId !== null && text;

  const handleFeedbackClick = () => {
    setIsFeedbackOpen((prev) => !prev);
  };

  return (
    <BaseBubble variant={variant} hasBackground={true} inMessageGroup={inMessageGroup}>
      {text && (
        <div className={variant} dangerouslySetInnerHTML={{ __html: sanitizedHtml }}/>
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
