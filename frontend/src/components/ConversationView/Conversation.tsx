import { useState } from "react";
import { MessageComposer } from "@/components/ConversationView/MessageComposer.tsx";
import { MessageBubble } from "@/components/ConversationView/MessageBubble.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";

export interface MessageProps {
  role: "user" | "agent";
  text: string;
}

const api = new ApiClient(authenticationProviderInstance);

export function Conversation() {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const [messages, setMessages] = useState([
    { role: "agent", text: "How can I help you today?" },
  ]);

  const onMessageComposerSubmit = async (message: string) => {
    setIsLoading(true);
    setMessages((currMessages) => [
      ...currMessages,
      { role: "user", text: message }
    ]);
    try {
      const apiAnswer = await api.getAnswer(conversationId, message);
      if (!apiAnswer) {
        setMessages((currMessages) => [
            ...currMessages,
            { role: "agent", text: "An error occurred. Please try again." },
        ]);
        return;
      }
      setMessages((currMessages) => [...currMessages, { role: "agent", text: apiAnswer.answer }]);
      setConversationId(apiAnswer.conversation_id);
    } catch (error) {
      console.error("Error fetching answer:", error);
    } finally {
      setIsLoading(false); // Ensure isLoading is reset after API call (even if api fails)
    }
  };

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex-grow flex-1 space-y-4">
        {messages.map((message, index) => (
          <MessageBubble key={index} text={message.text} variant={message.role === "user" ? "primary" : "secondary"} />
        ))}
      </div>
      <div className="flex-shrink-0">
        <MessageComposer onSubmit={onMessageComposerSubmit} isLoading={isLoading} />
      </div>
    </div>
  )
}