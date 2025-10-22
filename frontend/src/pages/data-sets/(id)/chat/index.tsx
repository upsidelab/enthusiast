import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {useApplicationContext} from "@/lib/use-application-context.ts";

import { NewChat } from "@/components/conversation-view/new-chat.tsx";
import { ChatSession } from "@/components/conversation-view/chat-session.tsx";

import type { Message } from "@/components/conversation-view/message-composer.tsx";

export type OnPendingMessage = (message: Message, conversationId: number) => void;

export function Chat() {
  const { dataSetId } = useApplicationContext()!;
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isNewChat = pathname === '/' || pathname.includes("/new");

  const [pendingMessage, setPendingMessage] = useState<Message>();

  const onPendingMessage: OnPendingMessage = (message, conversationId) => {
    setPendingMessage(message);
    navigate(`/data-sets/${dataSetId}/chat/${conversationId}`);
  }

  if (isNewChat) {
    return (<NewChat onPendingMessage={onPendingMessage}/>)
  }

  return (<ChatSession pendingMessage={pendingMessage} />)
}
