import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { NewConversation } from "@/components/conversation-view/new-conversation.tsx";
import {useApplicationContext} from "@/lib/use-application-context.ts";

export function NewChat() {
  const { availableAgents } = useApplicationContext()!;
  const { agent } = useParams();

  const agentId = agent ? parseInt(agent, 10) : null;
  const selectedAgent = availableAgents.find(agentObj => agentObj.id === agentId);
  const agentName = selectedAgent?.name ?? "Question Answer Agent";

  return (
    <PageMain className="h-full">
      <PageHeading title={agentName} description="Start a new conversation." className="sticky top-4 bg-white" />
      <NewConversation agentId={agent!} />
    </PageMain>
  );
}
