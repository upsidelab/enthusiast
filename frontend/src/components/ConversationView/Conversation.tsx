import { useEffect, useRef, useState } from "react";
import { MessageComposer } from "@/components/ConversationView/MessageComposer.tsx";
import { MessageBubble } from "@/components/ConversationView/MessageBubble.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";

export interface MessageProps {
  role: "user" | "agent";
  text: string;
  questionId: number | null;
}

const api = new ApiClient(authenticationProviderInstance);

export function Conversation() {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const lastMessageRef = useRef<HTMLDivElement | null>(null);

  const [messages, setMessages] = useState<MessageProps[]>([
    { role: "agent", text: "How can I help you today?", questionId: null },
  ]);

  const onMessageComposerSubmit = async (message: string) => {
    setIsLoading(true);
    setMessages((currMessages) => [
      ...currMessages,
      { role: "user", text: message, questionId: null }
    ]);
    setTimeout(() => {
      lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
    });
    try {
      const apiAnswer = await api.getAnswer(conversationId, message);
      if (!apiAnswer) {
        setMessages((currMessages) => [
            ...currMessages,
            { role: "agent", text: "An error occurred. Please try again.", questionId: null },
        ]);
        return;
      }
      setMessages((currMessages) => [...currMessages, { role: "agent", text: apiAnswer.answer, questionId: apiAnswer.message_id }]);
      setConversationId(apiAnswer.conversation_id);
    } catch (error) {
      console.error("Error fetching answer:", error);
    } finally {
      setIsLoading(false); // Ensure isLoading is reset after API call (even if api fails)
      setTimeout(() => {
        lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
      });
    }
  };

  useEffect(() => {
    setTimeout(() => {
      lastMessageRef.current?.scrollIntoView({behavior: "smooth"});
    });
  }, []);

  return (
    <div className="flex flex-col h-full px-4 pt-4">
      <div className="grow flex-1 space-y-4">
        {messages.map((message, index) => (
          <MessageBubble key={index} text={message.text} variant={message.role === "user" ? "primary" : "secondary"} questionId={message.questionId}/>
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
