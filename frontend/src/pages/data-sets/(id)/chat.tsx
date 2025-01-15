import { Conversation } from "@/components/conversation-view/conversation.tsx";
import { useParams } from "react-router-dom";

export function Chat() {
  const { chatId } = useParams();
  const conversationId = chatId ? Number(chatId) : null;

  return (
    <Conversation conversationId={conversationId} />
  );
}
