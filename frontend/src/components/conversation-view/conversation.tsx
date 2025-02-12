import { useEffect, useRef, useState } from "react";
import { MessageComposer } from "@/components/conversation-view/message-composer.tsx";
import { MessageBubble } from "@/components/conversation-view/message-bubble.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { MessageError } from "@/components/conversation-view/message-error.tsx";
import { useNavigate } from "react-router-dom";
import { WelcomePanel } from "@/components/conversation-view/welcome-panel.tsx";

export interface ConversationProps {
  conversationId: number | null;
}

export interface MessageProps {
  role: "user" | "agent" | "agent_error";
  text: string;
  id: number | null;
}

const api = new ApiClient(authenticationProviderInstance);

export function Conversation({ conversationId }: ConversationProps) {
  const [isLoading, setIsLoading] = useState(false);
  const lastMessageRef = useRef<HTMLDivElement | null>(null);
  const { dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();

  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [skipConversationReload, setSkipConversationReload] = useState(false);

  const onMessageComposerSubmit = async (message: string) => {
    setIsLoading(true);
    setMessages((currMessages) => [
      ...currMessages,
      { role: "user", text: message, id: null }
    ]);
    setTimeout(() => {
      lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
    });
    let currentConversationId = conversationId;
    if (!currentConversationId) {
      currentConversationId = await api.conversations().createConversation(dataSetId!);
      setSkipConversationReload(true);
      navigate(`/data-sets/${dataSetId}/chat/${currentConversationId}`);
    }
    const taskHandle = await api.conversations().sendMessage(currentConversationId, dataSetId!, message);

    const updateTaskStatus = async () => {
      try {
        const response = await api.conversations().fetchResponseMessage(currentConversationId!, taskHandle);
        if (response) {
          setMessages((currMessages) => [
            ...currMessages,
            response as MessageProps
          ]);
          setIsLoading(false);
          setTimeout(() => {
            lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
          });
        } else {
          setTimeout(updateTaskStatus, 2000);
        }
      } catch {
        setIsLoading(false);
      }
    }
    updateTaskStatus();
  };

  useEffect(() => {
    const loadInitialMessages = async () => {
      if (skipConversationReload) {
        setSkipConversationReload(false);
        return;
      }

      if (!conversationId) {
        setMessages([]);
        return;
      }

      const conversation = await api.conversations().getConversation(conversationId);
      const initialMessages = conversation.history as MessageProps[];
      setMessages(initialMessages);
    }

    loadInitialMessages();
    setTimeout(() => {
      lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
    });
  }, [conversationId]);

  if (!conversationId) {
    return <WelcomePanel onSendMessage={onMessageComposerSubmit} />;
  }

  return (
    <div className="flex flex-col h-full px-4 pt-4">
      <div className="grow flex-1 space-y-4">
        {messages.map((message, index) => (
          message.role == "agent_error" ?
            <MessageError key={index} text={message.text} /> :
            <MessageBubble key={index} text={message.text} variant={message.role === "user" ? "primary" : "secondary"} questionId={message.id}/>
        ))}
        <div className="mb-4" />
        <div ref={lastMessageRef} />
      </div>
      <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
        <MessageComposer onSubmit={onMessageComposerSubmit} isLoading={isLoading} />
      </div>
    </div>
  )
}
