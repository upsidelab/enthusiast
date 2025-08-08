import {MutableRefObject, useEffect, useRef, useState} from "react";
import {MessageComposer} from "@/components/conversation-view/message-composer.tsx";
import {MessageBubble} from "@/components/conversation-view/message-bubble.tsx";
import {authenticationProviderInstance} from "@/lib/authentication-provider.ts";
import {ApiClient, TaskHandle} from "@/lib/api.ts";
import {useApplicationContext} from "@/lib/use-application-context.ts";
import {MessageError} from "@/components/conversation-view/message-error.tsx";
import {MessageBubbleTyping} from "@/components/conversation-view/message-bubble-typing.tsx";

export interface ConversationProps {
    conversationId: number;
    onPendingMessageSent: () => void;
    pendingMessage: string | null;
}

export interface MessageProps {
    role: "human" | "ai" | "system";
    text: string;
    id: number | null;
}

interface ConversationUIProps {
    messages: MessageProps[];
    isAgentLoading: boolean
    agentAction: string;
    lastMessageRef: MutableRefObject<HTMLDivElement | null>
    onSubmit: (message: string) => void;
    isLoading: boolean;
}

function ConversationUI({messages, isAgentLoading, agentAction, lastMessageRef, onSubmit, isLoading}: ConversationUIProps) {
    return (
        <div className="flex flex-col h-full px-4 pt-16">
            <div className="grow flex-1 space-y-4">
                {messages.map((message, index) =>
                    message.role === "system" ? (
                        <MessageError key={index} text={message.text}/>
                    ) : (
                        <MessageBubble
                            key={index}
                            text={message.text}
                            variant={message.role === "human" ? "primary" : "secondary"}
                            questionId={message.id}
                        />
                    )
                )}
                {isAgentLoading && <MessageBubbleTyping text={agentAction}/>}
                <div className="mb-4"/>
                <div ref={lastMessageRef}/>
            </div>
            <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
                <MessageComposer onSubmit={onSubmit} isLoading={isLoading}/>
            </div>
        </div>
    );
}


const api = new ApiClient(authenticationProviderInstance);

const streamingEnabled = Boolean(import.meta.env.VITE_WS_BASE);

export function Conversation({ conversationId, pendingMessage, onPendingMessageSent }: ConversationProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [isAgentLoading, setIsAgentLoading] = useState(false);
    const [agentAction, setAgentAction] = useState<string>("Thinking...");
    const [messages, setMessages] = useState<MessageProps[]>([]);
    const initialized = useRef(false);

    const usePolling = useRef(!streamingEnabled);
    const lastMessageRef = useRef<HTMLDivElement | null>(null);
    const ws = useRef<WebSocket | null>(null);

    const { dataSetId } = useApplicationContext()!;

    // Cleanup WebSocket on unmount
    useEffect(() => {
        return () => {
            ws.current?.close();
        };
    }, []);

    // Load messages when conversationId changes
    useEffect(() => {
        const loadMessages = async () => {
            if (pendingMessage && !initialized.current) {
                // React StrictMode renders this component twice, but we can't execute this callback twice.
                initialized.current = true;
                await onMessageComposerSubmit(pendingMessage);
                onPendingMessageSent();
                setMessages([{role: "human", id: null, text: pendingMessage}]);
                return;
            }

            const conversation = await api.conversations().getConversation(conversationId);
            const initialMessages = conversation.history as MessageProps[];
            setMessages(initialMessages);

            setTimeout(() => {
                lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
            }, 100);
        };

        loadMessages();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [conversationId]);

    const scrollToLastMessage = () => {
        setTimeout(() => {
            lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
        });
    };

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

                    if (lastMessage && lastMessage.role === "ai" && lastMessage.id === null) {
                        return [
                            ...prevMessages.slice(0, -1),
                            { ...lastMessage, text: lastMessage.text + data.data.chunk }
                        ];
                    } else {
                        return [...prevMessages, { role: "ai", text: data.data.chunk, id: null }];
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
                    { role: "system", text: data.data.output, id: null },
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
                    { role: "ai", text: response.text, id: response.id }
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
            { role: "human", text: message, id: null }
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
        <ConversationUI
            messages={messages}
            isAgentLoading={isAgentLoading}
            agentAction={agentAction}
            lastMessageRef={lastMessageRef}
            onSubmit={onMessageComposerSubmit}
            isLoading={isLoading}
        />
    );
}
