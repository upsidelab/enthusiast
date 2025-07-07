import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { NewConversation } from "@/components/conversation-view/new-conversation.tsx";

export function NewChat() {
  const { agent } = useParams();
  const agentId = agent ? agent : 'Question Answer Agent';

  return (
    <PageMain className="h-full">
      <PageHeading title={agentId} description="Start a new conversation." className="sticky top-4 bg-white" />
      <NewConversation agent={agentId} />
    </PageMain>
  );
}
