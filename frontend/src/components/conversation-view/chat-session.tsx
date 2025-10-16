import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PlusIcon } from "lucide-react";
import { ApiClient, TaskHandle } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";

import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { Button } from "@/components/ui/button.tsx";
import { MessageBubble } from "@/components/conversation-view/message-bubble.tsx";
import { MessageError } from "@/components/conversation-view/message-error.tsx";
import { MessageBubbleTyping } from "@/components/conversation-view/message-bubble-typing.tsx";
import { ChatWindow } from "@/components/conversation-view/chat-window.tsx";

import { Conversation as ConversationSchema } from '@/lib/types.ts';

export interface MessageProps {
  type: "human" | "ai" | "system";
  text: string;
  id: number | null;
}

interface ChatSessionProps {
  pendingMessage: string;
}

const api = new ApiClient(authenticationProviderInstance);
const streamingEnabled = Boolean(import.meta.env.VITE_WS_BASE);

export function ChatSession({ pendingMessage }: ChatSessionProps) {
  const { chatId } = useParams();
  const { dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();

  const [conversation, setConversation] = useState<ConversationSchema | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAgentLoading, setIsAgentLoading] = useState(false);
  const [agentAction, setAgentAction] = useState<string>("Thinking...");
  const [messages, setMessages] = useState<MessageProps[]>([]);

  const initialized = useRef(false);
  const usePolling = useRef(!streamingEnabled);
  const lastMessageRef = useRef<HTMLDivElement | null>(null);
  const ws = useRef<WebSocket | null>(null);

  const conversationId = Number(chatId);
  const isAgentDeleted = !!conversation?.agent.deleted_at;
  const isAgentCorrupted = !!conversation?.agent.corrupted;

  const scrollToLastMessage = (timeout = 0) => {
    setTimeout(() => {
      lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }, timeout);
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      ws.current?.close();
    };
  }, []);

  // Load messages when conversationId changes
  useEffect(() => {
    const loadMessages = async () => {
      const initChat = pendingMessage && !initialized.current;

      if (initChat) {
        // React StrictMode renders this component twice, but we can't execute this callback twice.
        initialized.current = true;
        await onMessageComposerSubmit(pendingMessage);
        setMessages([{ type: "human", id: null, text: pendingMessage }]);
        return;
      }

      const conversation = await api.conversations().getConversation(conversationId);
      setConversation(conversation);

      if (!initChat) {
        const initialMessages = conversation.history as MessageProps[];
        setMessages(initialMessages);
      }

      scrollToLastMessage(100);
    };

    loadMessages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId]);

  const handleWebSocketMessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    const eventType = data.event;

    const handlers: Record<string, () => void> = {
      on_parser_start: () => {
        setIsAgentLoading(true);
      },
      on_parser_stream: () => {
        setIsLoading(false);
        setIsAgentLoading(false);

        setMessages((prevMessages) => {
          const lastMessage = prevMessages[prevMessages.length - 1];

          if (lastMessage && lastMessage.type === "ai" && lastMessage.id === null) {
            return [
              ...prevMessages.slice(0, -1),
              { ...lastMessage, text: lastMessage.text + data.data.chunk }
            ];
          } else {
            return [...prevMessages, { type: "ai", text: data.data.chunk, id: null }];
          }
        });

        scrollToLastMessage();
      },
      message_id: () => {
        setMessages((prevMessages) => {
          const lastMessage = prevMessages[prevMessages.length - 1];
          lastMessage.id = data.data.output;
          return [...prevMessages.slice(0, -1), lastMessage];
        });
      },
      action: () => {
        setAgentAction(data.data.output);
      },
      error: () => {
        setIsLoading(false);
        setIsAgentLoading(false);
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: "system", text: data.data.output, id: null },
        ]);
      },
    };

    const handler = handlers[eventType];
    if (handler) {
      handler();
    } else if (data.error) {
      setIsLoading(false);
    }
  };

  const handleWebSocketError = () => {
    usePolling.current = true;
  };

  const handleWebSocketClose = (event: CloseEvent) => {
    if (!event.wasClean) {
      usePolling.current = true;
    }
  };

  const createWsConnection = (conversationId: number): Promise<boolean> => {
    return new Promise((resolve) => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        resolve(true);
        return;
      }

      if (ws.current) {
        ws.current.close();
      }

      ws.current = new WebSocket(`${import.meta.env.VITE_WS_BASE}/ws/chat/${conversationId}/`);

      ws.current.onopen = () => {
        resolve(true);
      };
      ws.current.onmessage = handleWebSocketMessage;
      ws.current.onerror = () => {
        handleWebSocketError();
        resolve(false);
      };
      ws.current.onclose = (event) => {
        handleWebSocketClose(event);
        resolve(false);
      };

      setTimeout(() => {
        if (ws.current && ws.current.readyState !== WebSocket.OPEN) {
          usePolling.current = true;
          ws.current.close();
          resolve(false);
        }
      }, 5000);
    });
  };

  const updateTaskStatus = async (conversationId: number, taskHandle: TaskHandle, streaming: boolean) => {
    if (streaming) {
      return;
    }

    try {
      const response = await api.conversations().fetchResponseMessage(conversationId!, taskHandle);

      if (response) {
        setIsAgentLoading(false);
        setMessages((prev) => [
          ...prev,
          { type: "ai", text: response.text, id: response.id }
        ]);
        setIsLoading(false);
        scrollToLastMessage();
      } else {
        setTimeout(() => updateTaskStatus(conversationId, taskHandle, streaming), 2000);
      }
    } catch {
      setIsLoading(false);
      setIsAgentLoading(false);
    }
  };

  const addUserMessage = (message: string) => {
    setMessages((prev) => [
      ...prev,
      { type: "human", text: message, id: null }
    ]);
    scrollToLastMessage();
  };

  const onMessageComposerSubmit = async (message: string) => {
    setIsLoading(true);
    setIsAgentLoading(true);
    addUserMessage(message);

    const taskHandle = await api.conversations().sendMessage(conversationId, dataSetId!, message, streamingEnabled);
    usePolling.current = !taskHandle.streaming;

    if (taskHandle.streaming) {
      const connected = await createWsConnection(conversationId);
      if (!connected) {
        usePolling.current = true;
      }
    }

    try {
      updateTaskStatus(conversationId, taskHandle, !usePolling.current);
    } catch {
      setIsLoading(false);
      setIsAgentLoading(false);
    }
  };

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
          <ChatWindow className="pt-16" onSubmit={onMessageComposerSubmit} isLoading={isLoading} conversationLocked={isAgentDeleted || isAgentCorrupted}>
            <div className="grow flex-1 space-y-4">
              {messages.map((message, index) =>
                message.type === "system" ? (
                  <MessageError key={index} text={message.text} />
                ) : (
                  <MessageBubble
                    key={index}
                    text={message.text}
                    variant={message.type === "human" ? "primary" : "secondary"}
                    questionId={message.id}
                  />
                )
              )}
              {isAgentLoading && <MessageBubbleTyping text={agentAction} />}
              <div className="mb-4" />
              <div ref={lastMessageRef} />
            </div>
          </ChatWindow>
        </>
      }
    </PageMain>
  );
}
