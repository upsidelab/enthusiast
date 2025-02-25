import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MessageComposer } from "@/components/conversation-view/message-composer.tsx";
import { MessageBubble } from "@/components/conversation-view/message-bubble.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { MessageError } from "@/components/conversation-view/message-error.tsx";
import { MessageBubbleTyping } from "@/components/conversation-view/message-bubble-typing.tsx";

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
  const [isAgentLoading, setIsAgentLoading] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (conversationId) {
      ws.current = new WebSocket(`${import.meta.env.VITE_WS_BASE}/ws/chat/${conversationId}/`);

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.event === "on_parser_start") {
          setIsAgentLoading(true);
        } else if (data.event === "on_parser_stream") {
          setMessages((prevMessages) => {
            const lastMessage = prevMessages[prevMessages.length - 1];
            if (lastMessage && lastMessage.role === "agent" && lastMessage.id === null) {
              return [
                ...prevMessages.slice(0, -1),
                { ...lastMessage, text: lastMessage.text + data.data.chunk }
              ];
            } else {
              return [...prevMessages, { role: "agent", text: data.data.chunk, id: null }];
            }
          });
          setTimeout(() => {
            lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
          });
        } else if (data.error) {
          console.error("Error from server:", data.error);
          setMessages((prevMessages) => [
            ...prevMessages,
            { role: "agent_error", text: "An error occurred", id: null }
          ]);
          setIsLoading(false);
        }
      };

      return () => {
        ws.current?.close();
      };
    }
  }, [conversationId]);

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
    ws.current?.send(JSON.stringify({ message }));

    const updateTaskStatus = async () => {
      try {
        const response = await api.conversations().fetchResponseMessage(currentConversationId!, taskHandle);
        if (response) {
          setIsAgentLoading(false);
          setMessages((prevMessages) => {
            return prevMessages.map((msg) =>
              msg.id === null && msg.role === "agent"
                ? { ...msg, id: response.id, text: response.text }
                : msg
            );
          });
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

  return (
    <div className="flex flex-col h-full px-4 pt-4">
      <div className="grow flex-1 space-y-4">
        {messages.map((message, index) => (
          message.role == "agent_error" ?
            <MessageError key={index} text={message.text} /> :
            <MessageBubble key={index} text={message.text} variant={message.role === "user" ? "primary" : "secondary"} questionId={message.id}/>
        ))}
        {isAgentLoading && messages[messages.length - 1]?.role !== "agent" && <MessageBubbleTyping />}
        <div className="mb-4" />
        <div ref={lastMessageRef} />
      </div>
      <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
        <MessageComposer onSubmit={onMessageComposerSubmit} isLoading={isLoading} />
      </div>
    </div>
  )
}
