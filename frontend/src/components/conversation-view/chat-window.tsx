import React from "react";
import { MessageComposer } from "@/components/conversation-view/message-composer.tsx";
import { cn } from "@/lib/utils";

interface ChatWindowProps {
  children: React.ReactNode;
  className?: string;
  onSubmit: (message: string) => void;
  isLoading: boolean;
  conversationLocked?: boolean;
}

export function ChatWindow({ children, className, onSubmit, isLoading, conversationLocked }: ChatWindowProps) {
  return (
    <div className={cn("flex flex-col h-full px-4", className)}>
      {children}
      <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
        <MessageComposer onSubmit={onSubmit} isLoading={isLoading} conversationLocked={conversationLocked} />
      </div>
    </div>
  );
}
