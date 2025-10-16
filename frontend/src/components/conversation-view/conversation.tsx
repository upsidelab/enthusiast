import {MutableRefObject, useEffect, useRef, useState} from "react";
import {MessageComposer} from "@/components/conversation-view/message-composer.tsx";
import {MessageBubble} from "@/components/conversation-view/message-bubble.tsx";
import {AttachmentBubble} from "@/components/conversation-view/attachment-bubble.tsx";
import {authenticationProviderInstance} from "@/lib/authentication-provider.ts";
import {ApiClient, TaskHandle} from "@/lib/api.ts";
import {useApplicationContext} from "@/lib/use-application-context.ts";
import {MessageError} from "@/components/conversation-view/message-error.tsx";
import {MessageBubbleTyping} from "@/components/conversation-view/message-bubble-typing.tsx";

export interface ConversationProps {
    conversationId: number;
    onPendingMessageSent: () => void;
    pendingMessage: string | null;
    conversationLocked?: boolean;
}

export interface MessageFile {
    id: number;
    filename: string;
    content_type: string;
    file_url: string;
}

export interface MessageProps {
    type: "human" | "ai" | "system";
    text: string;
    id: number | null;
    files?: MessageFile[];
}

interface ConversationUIProps {
    messages: MessageProps[];
    isAgentLoading: boolean
    agentAction: string;
    lastMessageRef: MutableRefObject<HTMLDivElement | null>
    onSubmit: (message: string, fileIds?: number[]) => void;
    isLoading: boolean;
    conversationLocked?: boolean;
    conversationId?: number;
    agentId?: number;
}

function ConversationUI({messages, isAgentLoading, agentAction, lastMessageRef, onSubmit, isLoading, conversationLocked = false, conversationId, agentId}: ConversationUIProps) {
    return (
        <div className="flex flex-col h-full px-4 pt-16">
            <div className="grow flex-1 space-y-4">
                {messages.map((message, index) =>
                    message.type === "system" ? (
                        <MessageError key={index} text={message.text}/>
                    ) : !message.text && message.files && message.files.length > 0 ? (
                        <AttachmentBubble
                            key={index}
                            variant={message.type === "human" ? "primary" : "secondary"}
                            files={message.files}
                        />
                    ) : (
                        <MessageBubble
                            key={index}
                            text={message.text}
                            variant={message.type === "human" ? "primary" : "secondary"}
                            questionId={message.id}
                            files={message.files}
                        />
                    )
                )}
                {isAgentLoading && <MessageBubbleTyping text={agentAction}/>}
                <div className="mb-4"/>
                <div ref={lastMessageRef}/>
            </div>
            <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
                <MessageComposer onSubmit={onSubmit} isLoading={isLoading} conversationLocked={conversationLocked} conversationId={conversationId} agentId={agentId}/>
            </div>
        </div>
    );
}


const api = new ApiClient(authenticationProviderInstance);

const streamingEnabled = Boolean(import.meta.env.VITE_WS_BASE);

export function Conversation({ conversationId, pendingMessage, onPendingMessageSent, conversationLocked = false }: ConversationProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [isAgentLoading, setIsAgentLoading] = useState(false);
    const [agentAction, setAgentAction] = useState<string>("Thinking...");
    const [messages, setMessages] = useState<MessageProps[]>([]);
    const [agentId, setAgentId] = useState<number | undefined>();
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

    const onMessageComposerSubmit = async (message: string, fileIds?: number[]) => {
        setIsLoading(true);
        setIsAgentLoading(true);
        addUserMessage(message);

        const taskHandle = await api.conversations().sendMessage(conversationId, dataSetId!, message, streamingEnabled, fileIds);
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

    useEffect(() => {
        const loadMessages = async () => {
            if (pendingMessage && !initialized.current) {
                initialized.current = true;
                await onMessageComposerSubmit(pendingMessage);
                onPendingMessageSent();
                setMessages([{type: "human", id: null, text: pendingMessage}]);
                return;
            }

            const conversation = await api.conversations().getConversation(conversationId);
            const initialMessages = conversation.history as MessageProps[];
            setMessages(initialMessages);
            setAgentId(conversation.agent?.id);

            setTimeout(() => {
                lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
            }, 100);
        };

        loadMessages();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [conversationId]);

        return (
            <ConversationUI
                messages={messages}
                isAgentLoading={isAgentLoading}
                agentAction={agentAction}
                lastMessageRef={lastMessageRef}
                onSubmit={onMessageComposerSubmit}
                isLoading={isLoading}
                conversationLocked={conversationLocked}
                conversationId={conversationId}
                agentId={agentId}
            />
        );
}
