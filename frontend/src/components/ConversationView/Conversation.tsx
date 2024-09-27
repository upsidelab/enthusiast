import { useState } from "react";
import { MessageComposer } from "@/components/ConversationView/MessageComposer.tsx";
import { MessageBubble } from "@/components/ConversationView/MessageBubble.tsx";

export interface MessageProps {
  role: "user" | "agent";
  text: string;
}

export function Conversation() {
  const [messages, setMessages] = useState([
    { role: "agent", text: "How can I help you today?" },
    { role: "user", text: "Write a facebook ad promoting the new t-shirt with palm tree print" }
  ]);

  const onMessageComposerSubmit = (message: string) => {
    setMessages(
      [...messages, { role: "user", text: message }]
    );
  };

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex-grow flex-1 space-y-4">
        {messages.map((message, index) => (
          <MessageBubble key={index} text={message.text} variant={message.role === "user" ? "primary" : "secondary"} />
        ))}
      </div>
      <div className="flex-shrink-0">
        <MessageComposer onSubmit={onMessageComposerSubmit} />
      </div>
    </div>
  )
}
