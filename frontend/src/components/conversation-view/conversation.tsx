import {MutableRefObject, useEffect, useRef, useState} from "react";
import {MessageComposer} from "@/components/conversation-view/message-composer.tsx";
import {MessageBubble} from "@/components/conversation-view/message-bubble.tsx";
import {authenticationProviderInstance} from "@/lib/authentication-provider.ts";
import {ApiClient, TaskHandle} from "@/lib/api.ts";
import {useApplicationContext} from "@/lib/use-application-context.ts";
import {MessageError} from "@/components/conversation-view/message-error.tsx";
import {useNavigate} from "react-router-dom";
import {MessageBubbleTyping} from "@/components/conversation-view/message-bubble-typing.tsx";

export interface ConversationProps {
    conversationId: number | null;
}

export interface MessageProps {
    role: "user" | "agent" | "agent_error";
    text: string;
    id: number | null;
}

interface ConversationUIProps {
    messages: MessageProps[];
    isAgentLoading: boolean;
    lastMessageRef: MutableRefObject<HTMLDivElement | null>
    onSubmit: (message: string) => void;
    isLoading: boolean;
}

function ConversationUI({messages, isAgentLoading, lastMessageRef, onSubmit, isLoading}: ConversationUIProps) {
    return (
        <div className="flex flex-col h-full px-4 pt-4">
            <div className="grow flex-1 space-y-4">
                {messages.map((message, index) =>
                    message.role === "agent_error" ? (
                        <MessageError key={index} text={message.text}/>
                    ) : (
                        <MessageBubble
                            key={index}
                            text={message.text}
                            variant={message.role === "user" ? "primary" : "secondary"}
                            questionId={message.id}
                        />
                    )
                )}
                {isAgentLoading && <MessageBubbleTyping/>}
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

export function Conversation({ conversationId }: ConversationProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [isAgentLoading, setIsAgentLoading] = useState(false);
    const [messages, setMessages] = useState<MessageProps[]>([]);
    const [pendingMessage, setPendingMessage] = useState<string | null>(null);

    const usePolling = useRef(!streamingEnabled);
    const lastMessageRef = useRef<HTMLDivElement | null>(null);
    const ws = useRef<WebSocket | null>(null);

    const { dataSetId } = useApplicationContext()!;
    const navigate = useNavigate();

    // Cleanup WebSocket on unmount
    useEffect(() => {
        return () => {
            ws.current?.close();
        };
    }, []);

    // Load messages when conversationId changes
    useEffect(() => {
        const loadMessages = async () => {
            if (!conversationId) {
                setMessages([]);
                return;
            }

            if (pendingMessage) {
                onMessageComposerSubmit(pendingMessage);
                setPendingMessage(null);
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
    }, [conversationId]);

    const scrollToLastMessage = () => {
        setTimeout(() => {
            lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
        });
    };

    const handleWebSocketMessage = (event: MessageEvent) => {
        const data = JSON.parse(event.data);

        if (data.event === "on_parser_start") {
            setIsAgentLoading(true);
        } else if (data.event === "on_parser_stream") {
            setIsLoading(false);
            setIsAgentLoading(false);

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

            scrollToLastMessage();
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
                    { role: "agent", text: response.text, id: response.id }
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
            { role: "user", text: message, id: null }
        ]);
        scrollToLastMessage();
    };

    const onMessageComposerSubmit = async (message: string) => {
        if (!conversationId) {
            const newConversationId = await api.conversations().createConversation(dataSetId!);
            setPendingMessage(message);
            navigate(`/data-sets/${dataSetId}/chat/${newConversationId}`);
            return;
        }

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
            lastMessageRef={lastMessageRef}
            onSubmit={onMessageComposerSubmit}
            isLoading={isLoading}
        />
    );
}
