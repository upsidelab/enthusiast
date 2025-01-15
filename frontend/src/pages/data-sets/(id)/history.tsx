import { ConversationsList } from "@/components/conversations/conversations-list.tsx";

export function ChatHistory() {
  return (
    <div className="p-4">
      <ConversationsList />
    </div>
  );
}
