import { BaseBubble } from './base-bubble';
import { MessageFiles } from './message-files';
import { MessageFile } from './conversation';

interface AttachmentBubbleProps {
  variant: "primary" | "secondary";
  files: MessageFile[];
}

export function AttachmentBubble({ variant, files }: AttachmentBubbleProps) {
  return (
    <BaseBubble variant={variant} hasBackground={false} className="px-0 py-0">
      <MessageFiles files={files} compact={true} />
    </BaseBubble>
  );
}
