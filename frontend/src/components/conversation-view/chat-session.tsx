import { useEffect, useRef, useState, useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PlusIcon } from "lucide-react";
import { ApiClient, TaskHandle } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";

import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { Button } from "@/components/ui/button.tsx";
import { MessageBubble } from "@/components/conversation-view/message-bubble.tsx";
import { AttachmentBubble } from "@/components/conversation-view/attachment-bubble.tsx";
import { MessageError } from "@/components/conversation-view/message-error.tsx";
import { MessageBubbleTyping } from "@/components/conversation-view/message-bubble-typing.tsx";
import { ChatWindow } from "@/components/conversation-view/chat-window.tsx";

import type { AgentDetails } from "@/lib/types";
import type { Conversation as ConversationSchema } from '@/lib/types.ts';
import type { Message, MessageFile } from "@/components/conversation-view/message-composer.tsx";

import { Thread } from "@/components/assistant-ui/thread";
import { ThreadMessageLike } from "@assistant-ui/react";
import {
  AssistantRuntimeProvider,
  useExternalStoreRuntime,
} from "@assistant-ui/react";

export type FileMessageProps = {
  id: number | null;
  clientId: string;
  type: "file";
  file_name: string;
  file_type: string;
};

export type MessageProps = {
  type: "human" | "ai" | "system";
  text: string;
  id: number | null;
  clientId: string;
} | FileMessageProps;

interface ChatSessionProps {
  pendingMessage?: Message;
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
  const [agentId, setAgentId] = useState<number | undefined>();
  const [agentDetails, setAgentDetails] = useState<AgentDetails>();

  const initialized = useRef(false);
  const usePolling = useRef(!streamingEnabled);
  const lastMessageRef = useRef<HTMLDivElement | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const newClientId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

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

  useEffect(() => {
    const loadMessages = async () => {
      const initChat = pendingMessage && !initialized.current;

      if (initChat) {
        // React StrictMode renders this component twice, but we can't execute this callback twice.
        initialized.current = true;
        await onMessageComposerSubmit(pendingMessage);
      }

      const conversation = await api.conversations().getConversation(conversationId);
      setConversation(conversation);
      setAgentId(conversation.agent?.id);

      if (pendingMessage) {
        return;
      }

      const initialMessages = (conversation.history as any[]).map((message) => ({
        ...message,
        clientId: message.id,
      })) as MessageProps[];
      setMessages(initialMessages);

      scrollToLastMessage(100);
    };

    loadMessages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const loadAgentDetails = async () => {
      if (!agentId || agentDetails) {
        return;
      }

      try {
        const agentDetails = await api.agents().getAgentById(agentId);
        setAgentDetails(agentDetails);
      } catch (error) {
        console.error('Failed to load agent details:', error);
      }
    };

    loadAgentDetails();
  }, [agentId, agentDetails]);

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
            return [
              ...prevMessages,
              { type: "ai", text: data.data.chunk, id: null, clientId: newClientId() },
            ];
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
          { type: "ai", text: response.text, id: response.id, clientId: newClientId() }
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

  const addFileMessages = (files: MessageFile[]) => {
    const fileMessages = files.map<FileMessageProps>(file => ({
      id: null,
      clientId: newClientId(),
      type: "file",
      file_name: file.name,
      file_type: file.type
    }));

    setMessages((prev) => [ ...prev, ...fileMessages ]);
  }

  const addUserMessage = (message: string) => {
    setMessages((prev) => [
      ...prev,
      { type: "human", text: message, id: null, clientId: newClientId() }
    ]);
    scrollToLastMessage();
  };

  const onMessageComposerSubmit = async (message: Message) => {
    setIsLoading(true);
    setIsAgentLoading(true);
    addFileMessages(message.files);
    addUserMessage(message.text);

    const taskHandle = await api.conversations().sendMessage(conversationId, dataSetId!, message.text, streamingEnabled, message.files.map(f => f.id));
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

  const isUserMessage = (message: MessageProps) => {
    return message.type === "human" || message.type === "file";
  };

  // hacky POC

  type TextMessage = Exclude<MessageProps, FileMessageProps>;

  const convertMessage = (message: TextMessage): ThreadMessageLike => {
    const roleMap: Record<MessageProps['type'], ThreadMessageLike['role']> = {
      human: 'user',
      ai: 'assistant',
      system: 'system',
      file: 'user'
    };

    return {
      id: message.clientId,
      role: roleMap[message.type],
      content: message.text
    };
  };

  const runtime = useExternalStoreRuntime<TextMessage>({
    messages: messages.filter(m => m.type !== 'file') as TextMessage[],
    onNew: async (message) => {
      onMessageComposerSubmit({
        text: message?.content[0].text as string,
        files: []
      })
    },
    convertMessage,
    isRunning: isLoading
  });

  return (
    <PageMain className="h-full py-0">
      {conversation &&
        <>
          <PageHeading
              title={pendingMessage?.text || conversation.summary!}
              description={`Chat with ${conversation.agent.name}`}
              className="sticky top-0 pt-4 bg-white z-10"
          >
            <Button className="ml-auto mr-0" variant="outline" onClick={() => navigate(`/data-sets/${dataSetId}/chat/new/${encodeURIComponent(conversation.agent.id)}`)}>
              <PlusIcon />
              New Chat
            </Button>
          </PageHeading>
          <AssistantRuntimeProvider runtime={runtime}>
            <div className="overflow-hidden h-[90vh] -mt-6">
              <Thread/>
            </div>
          </AssistantRuntimeProvider>
        </>
      }
    </PageMain>
  );
}
