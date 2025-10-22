import { BaseBubble } from './base-bubble';
import { FileText, Image, File } from 'lucide-react';

import type { FileMessageProps } from './chat-session';

interface AttachmentBubbleProps {
  variant: "primary" | "secondary";
  message: FileMessageProps;
  inMessageGroup?: boolean;
}

const getFileIcon = (contentType: string) => {
  if (contentType.startsWith('image/')) {
    return <Image className="h-5 w-5" />;
  }
  if (contentType.includes('pdf') || contentType.includes('text')) {
    return <FileText className="h-5 w-5" />;
  }
  return <File className="h-5 w-5" />;
};

export function AttachmentBubble({ variant, message, inMessageGroup }: AttachmentBubbleProps ) {
  return (
    <BaseBubble variant={variant} hasBackground={false} className="px-0 py-0 min-w-[25%]" inMessageGroup={inMessageGroup}>
      <div
        className={`flex items-center space-x-2 rounded-md border shadow-sm px-3 py-2`}
      >
        <div className="h-8 w-8 bg-gray-200 rounded flex items-center justify-center">
          {getFileIcon(message.file_type)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">
            {message.file_name}
          </div>
          <div className="text-xs opacity-60">
            {message.file_type}
          </div>
        </div>
      </div>
    </BaseBubble>
  );
}
