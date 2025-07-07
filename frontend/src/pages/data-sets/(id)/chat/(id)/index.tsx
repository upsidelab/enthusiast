import { Conversation } from "@/components/conversation-view/conversation.tsx";
import { Conversation as ConversationSchema } from '@/lib/types.ts';
import { useParams, useSearchParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useEffect, useState } from "react";

const api = new ApiClient(authenticationProviderInstance);

export function Chat() {
  const { chatId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const conversationId = Number(chatId);
  const pendingMessage = searchParams.get("pending");
  const [conversation, setConversation] = useState<ConversationSchema | null>(null);

  const onPendingMessageSent = () => {
    setSearchParams({});
  }

  useEffect(() => {
    const fetchConversation = async () => {
      const apiConversation = await api.conversations().getConversation(conversationId);
      setConversation(apiConversation);
    }
    fetchConversation();
  }, [conversationId]);

  return (
    <PageMain className="h-full">
      {conversation &&
        <>
          <PageHeading title={pendingMessage || conversation.summary!} description={`Chat with ${conversation.agent}`} className="sticky top-0 p-4 bg-white" />
          <Conversation conversationId={conversationId} onPendingMessageSent={onPendingMessageSent} pendingMessage={pendingMessage} />
        </>
      }
    </PageMain>
  );
}
