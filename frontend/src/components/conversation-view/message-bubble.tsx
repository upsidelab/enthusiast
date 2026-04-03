import { useEffect, useState } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ChevronRightIcon, CheckIcon, XCircleIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { MessageFeedbackForm } from "@/components/message-feedback/message-feedback-form.tsx";
import { CopyToClipboardButton } from '@/components/conversation-view/copy-to-clipboard-button.tsx';
import { FeedbackButton } from '@/components/conversation-view/feedback-button.tsx';
import { BaseBubble } from '@/components/conversation-view/base-bubble';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import type { ToolStep } from '@/lib/types';

export interface MessageBubbleProps {
  text: string;
  variant: "primary" | "secondary";
  questionId: number | null;
  inMessageGroup?: boolean;
  steps?: ToolStep[];
}

export function MessageBubble({ text, variant, questionId, inMessageGroup, steps }: MessageBubbleProps) {
  const [sanitizedHtml, setSanitizedHtml] = useState<string>("");
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [isStepsOpen, setIsStepsOpen] = useState(false);

  useEffect(() => {
    const processText = async () => {
      const rawHtml = await marked(text);
      const cleanHtml = DOMPurify.sanitize(rawHtml);
      setSanitizedHtml(cleanHtml);
    };

    processText();
  }, [text]);

  const shouldShowActionButtons = variant === 'secondary' && questionId !== null && text;
  const hasSteps = variant === 'secondary' && steps && steps.length > 0;

  const handleFeedbackClick = () => {
    setIsFeedbackOpen((prev) => !prev);
  };

  return (
    <BaseBubble variant={variant} hasBackground={true} inMessageGroup={inMessageGroup}>
      {hasSteps && (
        <Collapsible open={isStepsOpen} onOpenChange={setIsStepsOpen}>
          <CollapsibleTrigger className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors mb-2 cursor-pointer">
            <ChevronRightIcon className={cn("w-3 h-3 transition-transform duration-200", isStepsOpen && "rotate-90")} />
            {steps!.length} tool{steps!.length > 1 ? 's' : ''} used
            {steps!.some(s => s.errored) && <XCircleIcon className="w-3 h-3 text-destructive ml-0.5" />}
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="border-l-2 border-muted-foreground/20 pl-3 space-y-1.5 mb-3">
              {steps!.map((step, i) => (
                <div key={i} className={cn("flex items-center gap-2 text-xs", step.errored ? "text-destructive" : "text-muted-foreground")}>
                  {step.errored ? (
                    <XCircleIcon className="w-3 h-3 shrink-0" />
                  ) : (
                    <CheckIcon className="w-3 h-3 shrink-0" />
                  )}
                  <span>{step.name}{step.input ? <span className="opacity-50"> — {step.input}</span> : null}</span>
                </div>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>
      )}

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
