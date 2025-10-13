import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {useApplicationContext} from "@/lib/use-application-context.ts";

import { NewChat } from "@/pages/data-sets/(id)/chat/new/(agent)/index.tsx";
import { Chat as ExistingChat } from "@/pages/data-sets/(id)/chat/(id)/index.tsx";

export type OnPendingMessage = (message: string, conversationId: number) => void;

export function Chat() {
  const { dataSetId } = useApplicationContext()!;
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isNewChat = pathname === '/' || pathname.includes("/new");

  const [pendingMessage, setPendingMessage] = useState<string>('');

  const onPendingMessage: OnPendingMessage = (message, conversationId) => {
    setPendingMessage(message);
    navigate(`/data-sets/${dataSetId}/chat/${conversationId}`);
  }

  if (isNewChat) {
    return (<NewChat onPendingMessage={onPendingMessage}/>)
  }

  return (<ExistingChat pendingMessage={pendingMessage} />)
}
