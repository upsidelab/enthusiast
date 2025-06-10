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

export function Conversation({conversationId}: ConversationProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [isAgentLoading, setIsAgentLoading] = useState(false);
    const [messages, setMessages] = useState<MessageProps[]>([]);
    const [skipConversationReload, setSkipConversationReload] = useState(false);
    const [usePolling, setUsePolling] = useState(!streamingEnabled);
    const lastMessageRef = useRef<HTMLDivElement | null>(null);
    const {dataSetId} = useApplicationContext()!;
    const navigate = useNavigate();
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        ws.current?.close()
    }, []);

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
    }, [conversationId, skipConversationReload]);

    const createWsConnection = (conversationId: number) => {
        ws.current = new WebSocket(`${import.meta.env.VITE_WS_BASE}/ws/chat/${conversationId}/`);
        ws.current.onmessage = (event) => {
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
                            {...lastMessage, text: lastMessage.text + data.data.chunk}
                        ];
                    } else {
                        return [...prevMessages, {role: "agent", text: data.data.chunk, id: null}];
                    }
                });
                setTimeout(() => {
                    lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
                });
            } else if (data.error) {
                setIsLoading(false);
            }
        };

        ws.current.onerror = () => {
            setUsePolling(true);
        };

        ws.current.onclose = (event) => {
            if (!event.wasClean) {
                setUsePolling(true);
            }
        };

        return () => {
            ws.current?.close();
        };
    }
    const updateTaskStatus = async (currentConversationId: number, taskHandle: TaskHandle, streaming: boolean) => {
        try {
            if (streaming) {
                return;
            }
            const response = await api.conversations().fetchResponseMessage(currentConversationId!, taskHandle);
            if (response) {
                setIsAgentLoading(false);
                setMessages((prev) => {
                            return [
                                ...prev,
                                {role: "agent", text: response.text, id: response.id}
                            ]
                    }
                );
                setIsLoading(false);
                setTimeout(() => {
                    lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
                });
            } else {
                setTimeout(() => updateTaskStatus(currentConversationId, taskHandle, streaming), 2000);
            }
        } catch {
            setIsLoading(false);
            setIsAgentLoading(false);
        }
    };

    const onMessageComposerSubmit = async (message: string) => {
        setIsLoading(true);
        setIsAgentLoading(true);
        setMessages((prev) => [
            ...prev,
            {role: "user", text: message, id: null}
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

        const taskHandle = await api.conversations().sendMessage(currentConversationId, dataSetId!, message, streamingEnabled);
        setUsePolling(!taskHandle.streaming)
        if (!usePolling) {
            createWsConnection(currentConversationId!);
            if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
                setUsePolling(true);
            }
        }
        try {
            updateTaskStatus(currentConversationId, taskHandle, !usePolling);
        } catch {
            setIsLoading(false);
            setIsAgentLoading(false);
        }
    }
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
