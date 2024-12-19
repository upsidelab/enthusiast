import { Conversation } from "@/components/ConversationView/Conversation.tsx";
import { useParams } from "react-router-dom";

export function Chat() {
  const { id } = useParams();
  const conversationId = id ? Number(id) : null;

  return (
    <Conversation conversationId={conversationId} />
  );
}
