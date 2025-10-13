import { Conversation } from "@/components/conversation-view/conversation.tsx";
import { Conversation as ConversationSchema } from '@/lib/types.ts';
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { PlusIcon } from "lucide-react";

const api = new ApiClient(authenticationProviderInstance);

interface ChatProps {
  pendingMessage: string;
}

export function Chat({ pendingMessage }: ChatProps) {
  const { chatId } = useParams();
  const { dataSetId } = useApplicationContext()!;
  const conversationId = Number(chatId);
  const [conversation, setConversation] = useState<ConversationSchema | null>(null);
  const navigate = useNavigate();

  const isAgentDeleted = !!conversation?.agent.deleted_at;
  const isAgentCorrupted = !!conversation?.agent.corrupted;

  useEffect(() => {
    const fetchConversation = async () => {
      const apiConversation = await api.conversations().getConversation(conversationId);
      setConversation(apiConversation);
    }
    fetchConversation();
  }, [conversationId]);

  return (
    <PageMain className="h-full py-0">
      {conversation &&
        <>
          <PageHeading
              title={pendingMessage || conversation.summary!}
              description={`Chat with ${conversation.agent.name}`}
              className="sticky top-0 pt-4 bg-white"
          >
            <Button className="ml-auto mr-0" variant="outline" onClick={() => navigate(`/data-sets/${dataSetId}/chat/new/${encodeURIComponent(conversation.agent.id)}`)}>
              <PlusIcon />
              New Chat
            </Button>
          </PageHeading>
          <Conversation conversationId={conversationId} pendingMessage={pendingMessage} conversationLocked={isAgentDeleted || isAgentCorrupted} />
        </>
      }
    </PageMain>
  );
}
